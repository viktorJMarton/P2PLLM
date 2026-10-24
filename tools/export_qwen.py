"""Prepare or execute the pinned Qwen0.6B export with a safetensors-only loader.

No provisioning or download is performed. Default invocation validates inputs
and prepares an isolated source patch; --execute additionally requires the
project-local export venv. Raw exporter output is discarded, never journalled.
"""

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import zipfile

try:
    from run_checks import WindowsJob, safe_path, CheckError
    from runtime_artifacts import verified_flatc, recheck_flatc, RuntimeArtifactError
except ModuleNotFoundError:
    from tools.run_checks import WindowsJob, safe_path, CheckError
    from tools.runtime_artifacts import verified_flatc, recheck_flatc, RuntimeArtifactError

ROOT = Path(__file__).resolve().parents[1]
REVISION = "3b60683923245cf472b7323426920e15623ba361"
MODEL_ID = "Qwen/Qwen3-0.6B"
PACKAGES = {"executorch": "1.5.1", "torch": "2.14.0", "torchao": "0.18.0",
            "transformers": "5.0.0rc1"}
MODEL_SOURCE = "examples/models/llama/model.py"
EXPORT_SOURCE = "examples/models/llama/export_llama_lib.py"
SOURCE_HASHES = {
    MODEL_SOURCE: "2b0a7abf044618feca96c10893b59a2066026c1147ed4fdfa84ac4232ba35249",
    EXPORT_SOURCE: "d5d1834a41031d849571bc8d4d59ad64532dbcc95d972bc05864e2794f597cc5",
}
CHECKPOINT_BLOCK = '''        if checkpoint_path:
            checkpoint = torch.load(checkpoint_path, map_location=device, mmap=True)
'''
SAFE_HELPERS = '''
def _qwen_reject_pickle(*args, **kwargs):
    raise ValueError("Model pickle loading is disabled by the pinned Qwen adapter")


def _qwen_load_safetensors(path, config):
    from pathlib import Path
    if config.base.model_class.value != "qwen3_0_6b":
        raise ValueError("Only pinned Qwen3-0.6B is supported")
    if config.base.lora_config or config.base.use_lora or config.base.preq_mode:
        raise ValueError("Adapters and prequantized inputs are disabled")
    if config.quantization.use_qat or config.quantization.use_spin_quant:
        raise ValueError("QAT and SpinQuant are disabled")
    if not path or Path(path).suffix != ".safetensors":
        raise ValueError("Explicit local safetensors checkpoint required")
    from safetensors.torch import load_file
    from executorch.examples.models.qwen3.convert_weights import qwen_3_tune_to_meta
    return qwen_3_tune_to_meta(load_file(path, device="cpu"))

'''


class ExportError(ValueError):
    """Bounded export precondition failure; never include untrusted diagnostics."""


KNOWN_EXPORT_REASONS = frozenset({
    "artifact_hash_mismatch", "artifact_missing_or_size_mismatch", "baseline_package_pin_mismatch",
    "baseline_revision_mismatch", "dependency_lock_digest_mismatch", "dependency_lock_incomplete",
    "dependency_lock_manifest_mismatch", "dependency_lock_not_fully_hashed",
    "dependency_lock_required_version_mismatch", "explicit_safetensors_required", "export_artifact_missing",
    "export_dependency_closure_unlocked_or_mismatched", "export_dependency_extra_or_url_not_supported",
    "export_dependency_lock_not_exact_closure", "export_dependency_version_mismatch",
    "export_forbidden_pickle_or_network", "export_imported_source_mismatch", "export_process_failed",
    "export_timeout", "installed_export_source_modified", "installed_original_backup_modified",
    "installed_patch_differs_from_source_patch", "installed_source_changed_before_export",
    "installed_source_changed_during_export", "isolated_export_venv_missing", "model_revision_mismatch",
    "official_export_wheel_missing_or_hash_mismatch", "official_wheel_patch_source_missing",
    "official_wheel_upstream_source_mismatch", "output_must_be_new_and_outside_checkout",
    "path_outside_artifacts", "pickle_call_remains", "resolved_hash_dependency_lock_missing",
    "single_checkpoint_required", "source_changed_during_export", "unexpected_export_venv",
    "unexpected_upstream_checkout_path", "unsafe_export_path", "unsupported_patch_target",
    "upstream_git_check_failed", "upstream_modified_patch_target", "upstream_patch_context_mismatch",
    "upstream_revision_mismatch", "upstream_source_hash_mismatch", "upstream_unexpected_modification",
    "flatc_artifact_verification_failed", "flatc_worker_recheck_failed",
})


def bounded_reason(error, fallback):
    # Never call exception __str__, including user-defined ExportError subclasses.
    if type(error) is ExportError and len(error.args) == 1:
        value = error.args[0]
        if type(value) is str and value in KNOWN_EXPORT_REASONS:
            return value
    return fallback


def _discard_log(*args, **kwargs):
    return None


def _empty_log_format(*args, **kwargs):
    return ""


def install_logging_guard():
    """Suppress Python logging emission in this dedicated export process.

    Hydra may reset levels/handlers after installation. Intercept actual logger
    and handler paths too, including late/direct FileHandler emission. Upstream
    fstrings can still evaluate in memory; native/direct file I/O is not an OS
    sandbox. Console streams are separately discarded by the worker launcher.
    """
    logging.disable(sys.maxsize)
    logging.Logger._log = _discard_log
    logging.Logger.handle = _discard_log
    logging.Handler.handle = _discard_log
    logging.Handler.format = _empty_log_format
    logging.StreamHandler.emit = _discard_log
    logging.FileHandler.emit = _discard_log


def exception_details(error):
    """Bounded trusted-source locations/types only; no message, source or locals."""
    trusted_roots = (ROOT / "tools", Path(sys.prefix) / "Lib", Path(sys.base_prefix) / "Lib")
    prefixes = ("builtins", "hydra", "omegaconf", "torch", "torchao", "executorch", "safetensors", "subprocess")
    chain, seen = [], set()
    current = error
    while current is not None and id(current) not in seen and len(chain) < 5:
        seen.add(id(current))
        cls = type(current)
        name = cls.__module__ + "." + cls.__qualname__
        if not (cls.__module__.split(".")[0] in prefixes and re.fullmatch(r"[A-Za-z0-9_.]{1,160}", name)):
            name = "ExportError" if cls is ExportError else "UnclassifiedError"
        frames = deque(maxlen=20)
        frame = current.__traceback__
        while frame is not None:
            code = frame.tb_frame.f_code
            path = Path(code.co_filename)
            if path.is_absolute() and any(path.is_relative_to(root) for root in trusted_roots):
                filename, function = path.name, code.co_name
                if re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", filename) and re.fullmatch(r"[A-Za-z0-9_.<>]{1,100}", function):
                    frames.append({"filename": filename, "function": function, "line": frame.tb_lineno})
            frame = frame.tb_next
        chain.append({"type": name, "frames": list(frames)})
        current = current.__cause__ if current.__cause__ is not None else current.__context__
    return {"chain": chain}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def patched_source(path, original, expected_hash):
    """Exact-byte upstream identity precedes any deterministic transformation."""
    if hashlib.sha256(original).hexdigest() != expected_hash:
        raise ExportError("upstream_source_hash_mismatch")
    text = original.decode("utf-8")
    if path == MODEL_SOURCE:
        if text.count(CHECKPOINT_BLOCK) != 1 or text.count("import torch\n") != 1:
            raise ExportError("upstream_patch_context_mismatch")
        text = text.replace(CHECKPOINT_BLOCK,
                            "        checkpoint = _qwen_load_safetensors(checkpoint_path, self.llm_config)\n")
        text = text.replace("torch.load(", "_qwen_reject_pickle(")
        text = text.replace("import torch\n", "import torch\n" + SAFE_HELPERS, 1)
        if "torch.load(" in text or "torch.save(" in text:
            raise ExportError("pickle_call_remains")
    elif path == EXPORT_SOURCE:
        old = "        checkpoint = download_and_convert_hf_checkpoint(repo_id, convert_weights)"
        if text.count(old) != 1:
            raise ExportError("upstream_patch_context_mismatch")
        text = text.replace(old, '        raise ValueError("Explicit offline safetensors checkpoint required")')
    else:
        raise ExportError("unsupported_patch_target")
    compile(text, path, "exec")
    return text.encode("utf-8")


def verify_artifact(path, entry):
    if not path.is_file() or path.is_symlink() or path.stat().st_size != entry["size_bytes"]:
        raise ExportError("artifact_missing_or_size_mismatch")
    if sha256(path) != entry["sha256"]:
        raise ExportError("artifact_hash_mismatch")


def artifact_path(root, value):
    if re.search(r'''[\x00-\x1f"'\[\]{}$,=]''', str(value)):
        raise ExportError("unsafe_export_path")
    path = safe_path(root, value)
    if not path.resolve().is_relative_to(root / ".artifacts"):
        raise ExportError("path_outside_artifacts")
    return path


def verify_checkout(checkout):
    def git(*args):
        result = subprocess.run(
            ["git", "-c", f"safe.directory={checkout.as_posix()}", *args],
            cwd=checkout, capture_output=True, text=True, timeout=30, check=False,
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        )
        if result.returncode:
            raise ExportError("upstream_git_check_failed")
        return result.stdout.rstrip("\r\n")
    if git("rev-parse", "HEAD") != REVISION:
        raise ExportError("upstream_revision_mismatch")
    changed = git("status", "--porcelain", "--untracked-files=normal").splitlines()
    allowed = set(SOURCE_HASHES) | {name + ".qwen-original" for name in SOURCE_HASHES}
    if any(line[3:] not in allowed for line in changed):
        raise ExportError("upstream_unexpected_modification")
    # Host export uses the verified official wheel; this source-only audit does
    # not establish Android runner/submodule build readiness.


def prepare_sources(checkout):
    """Validate both targets before mutating either; repeat preparation is safe."""
    updates = {}
    records = []
    for name, expected in SOURCE_HASHES.items():
        path = safe_path(checkout, name)
        # Original copies remain outside Python import paths and are hash checked.
        backup = path.with_suffix(path.suffix + ".qwen-original")
        safe_path(checkout, backup)
        original = backup.read_bytes() if backup.exists() else path.read_bytes()
        adapted = patched_source(name, original, expected)
        current = path.read_bytes()
        if current not in (original, adapted):
            raise ExportError("upstream_modified_patch_target")
        updates[path] = (backup, original, adapted)
        records.append({"path": name, "original_sha256": expected,
                        "adapted_sha256": hashlib.sha256(adapted).hexdigest()})
    for path, (backup, original, adapted) in updates.items():
        if not backup.exists():
            with backup.open("xb") as stream:
                stream.write(original)
        path.write_bytes(adapted)
    return records


def export_arguments(checkout, checkpoint, output):
    return ["--config", str(checkout / "examples/models/qwen3/config/qwen3_xnnpack_q8da4w.yaml"),
            '+base.model_class="qwen3_0_6b"',
            f'+base.params="{(checkout / "examples/models/qwen3/config/0_6b_config.json").as_posix()}"',
            f'+base.checkpoint="{checkpoint.as_posix()}"',
            f'+export.output_dir="{output.as_posix()}"',
            f'+export.output_name="{(output / "qwen3_0_6b.pte").as_posix()}"',
            "hydra/job_logging=disabled", "hydra/hydra_logging=disabled",
            "hydra.output_subdir=null", f'hydra.run.dir="{output.as_posix()}"']


def prepare_installed_sources(root, python, baseline, source_patches):
    """Adapt only the dedicated venv's verified official-wheel Python members.

    Windows wheel text uses CRLF: preserve its raw hash, compare canonical LF
    source with upstream, then apply the exact same deterministic source patch.
    Wheel/artifact hashes themselves are never newline-normalized.
    """
    venv = root / ".artifacts/venvs/qwen-export"
    if not python.resolve().is_relative_to(venv.resolve()):
        raise ExportError("unexpected_export_venv")
    resolution = baseline["runtime"]["dependency_resolution"]
    package = next(p for p in resolution["packages"] if p["name"] == "executorch")
    wheels = venv / "wheelhouse"
    wheel = next((p for p in wheels.glob("executorch-1.5.1-*.whl") if sha256(p) == package["sha256"]), None)
    if wheel is None:
        raise ExportError("official_export_wheel_missing_or_hash_mismatch")
    site = venv / ("Lib/site-packages" if os.name == "nt" else "lib/python3.12/site-packages")
    installed = artifact_path(root, site / "executorch")
    expected_patches = {p["path"]: p for p in source_patches}
    updates, records = [], []
    with zipfile.ZipFile(wheel) as archive:
        members = set(archive.namelist())
        for source in baseline["runtime"]["sources"]:
            name = source["path"]
            if Path(name).suffix not in (".py", ".yaml", ".json"):
                continue
            member = "executorch/" + name
            if member not in members:
                continue  # Explicit params/config not shipped in wheel remain checkout inputs.
            raw = archive.read(member)
            canonical = raw.replace(b"\r\n", b"\n")
            if hashlib.sha256(canonical).hexdigest() != source["sha256"]:
                raise ExportError("official_wheel_upstream_source_mismatch")
            path = artifact_path(root, installed / name)
            adapted = patched_source(name, canonical, SOURCE_HASHES[name]) if name in SOURCE_HASHES else raw
            if name in expected_patches and hashlib.sha256(adapted).hexdigest() != expected_patches[name]["adapted_sha256"]:
                raise ExportError("installed_patch_differs_from_source_patch")
            if not path.is_file() or path.read_bytes() not in (raw, adapted):
                raise ExportError("installed_export_source_modified")
            records.append({"path": name, "installed_path": str(path),
                            "wheel_member_raw_sha256": hashlib.sha256(raw).hexdigest(),
                            "upstream_canonical_sha256": source["sha256"],
                            "effective_sha256": hashlib.sha256(adapted).hexdigest()})
            if name in SOURCE_HASHES:
                updates.append((path, raw, adapted))
    if not set(SOURCE_HASHES).issubset({r["path"] for r in records}):
        raise ExportError("official_wheel_patch_source_missing")
    # Both original/installed members validated before either source write.
    for path, raw, adapted in updates:
        backup = artifact_path(root, path.with_suffix(path.suffix + ".qwen-wheel-original"))
        if backup.exists() and backup.read_bytes() != raw:
            raise ExportError("installed_original_backup_modified")
    for path, raw, adapted in updates:
        backup = path.with_suffix(path.suffix + ".qwen-wheel-original")
        if not backup.exists():
            with backup.open("xb") as stream:
                stream.write(raw)
        path.write_bytes(adapted)
    return installed, records


def canonical_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def read_dependency_lock(path, required, expected=None):
    """A reviewed complete one-line-per-wheel hash lock is an execution prerequisite."""
    if not path.is_file():
        raise ExportError("resolved_hash_dependency_lock_missing")
    versions = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)(?: --hash=sha256:[0-9a-f]{64})+", line)
        if not match or canonical_name(match[1]) in versions:
            raise ExportError("dependency_lock_not_fully_hashed")
        name = canonical_name(match[1])
        versions[name] = match[2]
        if expected is not None:
            entry = expected.get(name)
            if (entry is None or entry["version"] != match[2]
                    or re.findall(r"--hash=sha256:([0-9a-f]{64})", line) != [entry["sha256"]]):
                raise ExportError("dependency_lock_manifest_mismatch")
    if any(versions.get(name) != version for name, version in required.items()):
        raise ExportError("dependency_lock_required_version_mismatch")
    if expected is not None and set(versions) != set(expected):
        raise ExportError("dependency_lock_incomplete")
    return versions


def verify_dependency_closure(versions, roots, requires=None, version_of=None, parser=None):
    """Verify the installed relevant default-extra closure, not just four entries.

    Version/metadata checks assume a trusted venv installed from the reviewed
    wheel hash lock; they do not prove all installed wheel bytes are unchanged.
    """
    from importlib import metadata
    if parser is None:
        from packaging.requirements import Requirement
        parser = Requirement
    requires = requires or metadata.requires
    version_of = version_of or metadata.version
    pending, seen = list(roots), set()
    while pending:
        name = canonical_name(pending.pop())
        if name in seen:
            continue
        if name not in versions or version_of(name) != versions[name]:
            raise ExportError("export_dependency_closure_unlocked_or_mismatched")
        seen.add(name)
        for text in requires(name) or []:
            requirement = parser(text)
            if requirement.marker and not requirement.marker.evaluate({"extra": ""}):
                continue
            child = canonical_name(requirement.name)
            if requirement.url or requirement.extras:
                raise ExportError("export_dependency_extra_or_url_not_supported")
            if child not in versions or versions[child] not in requirement.specifier:
                raise ExportError("export_dependency_closure_unlocked_or_mismatched")
            pending.append(child)
    if seen != set(versions):
        raise ExportError("export_dependency_lock_not_exact_closure")
    return sorted(seen)


WORKER = '''import pathlib, runpy, sys
wrapper = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(wrapper.parent.parent))
module = runpy.run_path(str(wrapper), run_name="__qwen_export_worker__")
raise SystemExit(module["worker_main"](sys.argv[2:]))
'''


def forbidden_serialization(*args, **kwargs):
    raise ExportError("export_forbidden_pickle_or_network")


def deny_export_event(event, args):
    # Defense in depth for trusted pinned Python, not a native-code/OS sandbox.
    if event in ("socket.connect", "socket.getaddrinfo", "socket.sendto",
                 "socket.sendmsg", "pickle.find_class"):
        forbidden_serialization()


def worker_main(argv):
    """Trusted local export worker; no model data or raw exception text is saved."""
    install_logging_guard()
    from importlib import metadata
    import inspect
    import runpy
    checkout, output = Path(argv[0]), Path(argv[1])
    versions, source_records, flatc = json.loads(argv[2]), json.loads(argv[3]), json.loads(argv[4])
    args = argv[5:]
    result = {"status": "failed", "phase": "dependency_versions"}
    try:
        for package, version in versions.items():
            if metadata.version(package) != version:
                raise ExportError("export_dependency_version_mismatch")
        result["phase"] = "dependency_closure"
        verify_dependency_closure(versions, PACKAGES)
        result["phase"] = "flatbuffer_compiler"
        try:
            os.environ["FLATC_EXECUTABLE"] = recheck_flatc(flatc, Path(sys.prefix))
        except RuntimeArtifactError as error:
            raise ExportError("flatc_worker_recheck_failed") from error
        result["phase"] = "torch_import"
        import torch

        setattr(torch, "load", forbidden_serialization)
        setattr(torch, "save", forbidden_serialization)
        sys.addaudithook(deny_export_event)
        result["phase"] = "patched_source_import"
        for record in source_records:
            if sha256(Path(record["installed_path"])) != record["effective_sha256"]:
                raise ExportError("installed_source_changed_before_export")
        from executorch.examples.models.llama.model import Llama2Model
        expected = Path(next(r["installed_path"] for r in source_records if r["path"] == MODEL_SOURCE))
        if Path(inspect.getsourcefile(Llama2Model)).resolve() != expected.resolve():
            raise ExportError("export_imported_source_mismatch")
        result["phase"] = "export_pipeline"
        sys.argv = ["export_llm"] + args
        runpy.run_module("executorch.extension.llm.export.export_llm", run_name="__main__")
        result.update(status="passed", phase="complete")
        return 0
    except KeyboardInterrupt:
        result.update(status="interrupted", reason="export_cancelled")
        return 130
    except Exception as error:
        result["reason"] = bounded_reason(error, "export_worker_failed")
        result["error_details"] = exception_details(error)
        return 1
    except SystemExit as error:
        result["reason"] = "export_entry_exited"
        result["error_details"] = exception_details(error)
        return 1
    finally:
        with (output / "worker-result.json").open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")


def execute_export(python, checkout, checkpoint, output, versions, source_records, flatc, timeout=1800):
    install_logging_guard()
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
    env.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1", HYDRA_FULL_ERROR="1",
               HF_HUB_DISABLE_TELEMETRY="1", PYTHONDONTWRITEBYTECODE="1",
               PYTHONNOUSERSITE="1", PYTHONSAFEPATH="1")
    argv = [str(python), "-c", WORKER, str(Path(__file__)), str(checkout), str(output), json.dumps(versions),
            json.dumps(source_records), json.dumps(flatc), *export_arguments(checkout, checkpoint, output)]
    process = job = None
    try:
        job = WindowsJob() if os.name == "nt" else None
        with open(os.devnull, "wb") as discarded:
            process = subprocess.Popen(argv, cwd=checkout, env=env, shell=False,
                                       stdout=discarded, stderr=discarded,
                                       start_new_session=os.name != "nt")
            if job:
                job.assign(process)
            code = process.wait(timeout=timeout)
        if code:
            raise ExportError("export_process_failed")
    except subprocess.TimeoutExpired as error:
        raise ExportError("export_timeout") from error
    finally:
        if job:
            job.close()
        elif process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=10)


def run(args, root=ROOT):
    install_logging_guard()
    baseline = json.loads((root / "config/model-baselines.json").read_text(encoding="utf-8"))
    if baseline["runtime"]["revision"] != REVISION:
        raise ExportError("baseline_revision_mismatch")
    model = next(m for m in baseline["models"] if m["repo_id"] == MODEL_ID)
    if model["revision"] != "c1899de289a04d12100db370d81485cdf75e47ca":
        raise ExportError("model_revision_mismatch")
    checkout = artifact_path(root, args.upstream_dir)
    if checkout != root / ".artifacts/upstream" / ("executorch-" + REVISION):
        raise ExportError("unexpected_upstream_checkout_path")
    checkpoint = artifact_path(root, args.checkpoint)
    tokenizer_dir = artifact_path(root, args.tokenizer_dir)
    output = artifact_path(root, args.output_dir)
    if checkpoint.suffix != ".safetensors" or checkpoint.name != "model.safetensors":
        raise ExportError("explicit_safetensors_required")
    if len(model["weight_artifacts"]) != 1:
        raise ExportError("single_checkpoint_required")
    verify_artifact(checkpoint, model["weight_artifacts"][0])
    for entry in model["files"]:
        verify_artifact(artifact_path(root, tokenizer_dir / entry["path"]), entry)
    verify_checkout(checkout)
    for entry in baseline["runtime"]["sources"]:
        if entry["path"] not in SOURCE_HASHES:
            verify_artifact(artifact_path(root, checkout / entry["path"]), entry)
    if output.exists() or output == checkout or checkout in output.parents:
        raise ExportError("output_must_be_new_and_outside_checkout")
    patches = prepare_sources(checkout)
    output.mkdir(parents=True, exist_ok=False)
    report = {"schema_version": 1, "work_id": "WORK-0002",
              "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "prepared_not_exported", "model_repo_id": MODEL_ID,
              "model_revision": model["revision"], "runtime_revision": REVISION,
              "checkpoint_sha256": model["weight_artifacts"][0]["sha256"],
              "tokenizer_files": model["files"], "patches": patches,
              "export_recipe": {**baseline["runtime"]["export_recipe"],
                                "loader_status": "pinned_safetensors_adapter_prepared"},
              "wrapper_sha256": sha256(Path(__file__)), "backend_placement": "unverified",
              "phone_measurement_performed": False}
    try:
        if args.execute:
            relative = "Scripts/python.exe" if os.name == "nt" else "bin/python"
            python = artifact_path(root, root / ".artifacts/venvs/qwen-export" / relative)
            if not python.is_file():
                raise ExportError("isolated_export_venv_missing")
            required = {p["name"]: p["version"] for p in baseline["runtime"]["host_package_candidates"]}
            if required != PACKAGES:
                raise ExportError("baseline_package_pin_mismatch")
            lock = artifact_path(root, root / ".artifacts/venvs/qwen-export/requirements.lock")
            resolution = baseline["runtime"]["dependency_resolution"]
            if sha256(lock) != resolution["lock_sha256"]:
                raise ExportError("dependency_lock_digest_mismatch")
            expected = {p["name"]: p for p in resolution["packages"]}
            versions = read_dependency_lock(lock, required, expected)
            report["dependency_lock_sha256"] = sha256(lock)
            installed, source_records = prepare_installed_sources(root, python, baseline, patches)
            report["installed_export_package"] = str(installed)
            report["installed_source_records"] = source_records
            report["host_export_route"] = "verified_official_wheel_with_pinned_safetensors_adapter"
            try:
                flatc = verified_flatc(root, baseline, python)
            except RuntimeArtifactError as error:
                raise ExportError("flatc_artifact_verification_failed") from error
            report["flatc"] = flatc
            execute_export(python, checkout, checkpoint, output, versions, source_records, flatc)
            verify_artifact(checkpoint, model["weight_artifacts"][0])
            for entry in model["files"]:
                verify_artifact(tokenizer_dir / entry["path"], entry)
            for patch in patches:
                if sha256(checkout / patch["path"]) != patch["adapted_sha256"]:
                    raise ExportError("source_changed_during_export")
            for record in source_records:
                if sha256(Path(record["installed_path"])) != record["effective_sha256"]:
                    raise ExportError("installed_source_changed_during_export")
            artifact = output / "qwen3_0_6b.pte"
            if not artifact.is_file() or artifact.stat().st_size == 0:
                raise ExportError("export_artifact_missing")
            report.update(status="exported_not_reference_or_device_verified",
                          pte_sha256=sha256(artifact), pte_size_bytes=artifact.stat().st_size)
    except KeyboardInterrupt:
        report.update(status="interrupted", reason="export_cancelled")
        raise
    except (ExportError, OSError, subprocess.SubprocessError) as error:
        report["status"] = "failed"
        report["reason"] = bounded_reason(error, "export_process_or_io_failed")
        report["error_details"] = exception_details(error)
        raise
    finally:
        with (output / "export-provenance.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    return report


def main():
    install_logging_guard()
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("upstream-dir", "checkpoint", "tokenizer-dir", "output-dir"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        report = run(args)
    except KeyboardInterrupt:
        print(json.dumps({"status": "interrupted", "reason": "export_cancelled"}))
        return 130
    except (ExportError, CheckError, OSError, ValueError, KeyError, StopIteration,
            subprocess.SubprocessError) as error:
        # Only our fixed reason codes are emitted; arbitrary exception text is private.
        reason = bounded_reason(error, "export_precondition_or_io_failed")
        print(json.dumps({"status": "failed", "reason": reason}))
        return 1
    print(json.dumps({"status": report["status"], "phone_measurement_performed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
