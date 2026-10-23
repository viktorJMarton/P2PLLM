"""Safety tests use synthetic source/tensor stubs; never load a model or network."""

import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
import zipfile
from unittest.mock import patch
from pip._vendor.packaging.requirements import Requirement

from tools import export_qwen as export


def config(**updates):
    result = SimpleNamespace(
        base=SimpleNamespace(model_class=SimpleNamespace(value="qwen3_0_6b"),
                             lora_config=None, use_lora=0, preq_mode=None),
        quantization=SimpleNamespace(use_qat=False, use_spin_quant=None),
    )
    for section, key, value in updates.get("fields", []):
        setattr(getattr(result, section), key, value)
    return result


class SafeLoaderTests(unittest.TestCase):
    def setUp(self):
        namespace = {}
        exec(export.SAFE_HELPERS, namespace)
        self.load = namespace["_qwen_load_safetensors"]
        self.reject = namespace["_qwen_reject_pickle"]

    def test_load_and_mapping_are_in_memory_and_cpu_only(self):
        tensors = {"synthetic": object()}
        calls = []
        safe = ModuleType("safetensors.torch")
        safe.load_file = lambda path, device: calls.append((path, device)) or tensors
        mapping = ModuleType("executorch.examples.models.qwen3.convert_weights")
        mapping.qwen_3_tune_to_meta = lambda value: {"mapped": value["synthetic"]}
        with patch.dict(sys.modules, {"safetensors.torch": safe,
                                      "executorch.examples.models.qwen3.convert_weights": mapping}):
            result = self.load("model.safetensors", config())
        self.assertIs(result["mapped"], tensors["synthetic"])
        self.assertEqual(calls, [("model.safetensors", "cpu")])

    def test_pickle_missing_and_other_formats_fail_before_import(self):
        for path in (None, "weights.pt", "weights.pth", "weights.bin", "model.safetensors.pkl"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.load(path, config())
        with self.assertRaises(ValueError):
            self.reject("any.pt")

    def test_unsupported_model_and_training_branches_are_rejected(self):
        cases = [("base", "lora_config", object()), ("base", "use_lora", 1),
                 ("base", "preq_mode", "8da4w"), ("quantization", "use_qat", True),
                 ("quantization", "use_spin_quant", "native")]
        for field in cases:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.load("model.safetensors", config(fields=[field]))
        wrong = config()
        wrong.base.model_class.value = "qwen3_1_7b"
        with self.assertRaises(ValueError):
            self.load("model.safetensors", wrong)

    def test_worker_python_event_guard_rejects_udp_connect_dns_and_pickle(self):
        for event in ("socket.connect", "socket.getaddrinfo", "socket.sendto",
                      "socket.sendmsg", "pickle.find_class"):
            with self.subTest(event=event), self.assertRaises(export.ExportError):
                export.deny_export_event(event, ())
        export.deny_export_event("open", ())
        with self.assertRaises(export.ExportError):
            export.forbidden_serialization("not-loaded.pt")


class LoggingAndDiagnosticTests(unittest.TestCase):
    def test_logging_guard_survives_reconfiguration_and_direct_late_handlers(self):
        # A child isolates permanent process-level logging suppression from the
        # rest of the test runner. Canary data are synthetic, never model data.
        code = r'''
import json, logging, logging.config, pathlib, tempfile
from tools import export_qwen as export
class Canary:
    def __str__(self):
        raise AssertionError("logging must not format lazy payloads")
class Formatter(logging.Formatter):
    def format(self, record):
        raise AssertionError("logging formatter must not be reached")
with tempfile.TemporaryDirectory() as temporary:
    path = pathlib.Path(temporary) / "late.log"
    export.install_logging_guard()
    logging.config.dictConfig({"version":1,"disable_existing_loggers":False,
        "handlers":{"late":{"class":"logging.FileHandler","filename":str(path)}},
        "root":{"level":"DEBUG","handlers":["late"]}})
    logging.disable(0)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("prompt/tensor %s", Canary())
    logging.info(f"inputs: {'SYNTHETIC_TENSOR_CANARY'}")
    record = logging.LogRecord("fixture",logging.INFO,"fixture.py",1,Canary(),(),None)
    logging.getLogger().handle(record)
    late = logging.FileHandler(path)
    late.setFormatter(Formatter())
    late.handle(record)
    late.emit(record)
    logging.StreamHandler().emit(record)
    late.close()
    logging.shutdown()
    assert path.read_bytes() == b""
print(json.dumps({"guard_canary_passed":True}))
'''
        result = subprocess.run([sys.executable, "-c", code], cwd=export.ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {"guard_canary_passed": True})
        self.assertNotIn("SYNTHETIC_TENSOR_CANARY", result.stdout + result.stderr)

    def test_exception_chains_have_no_message_source_locals_path_or_exit_code(self):
        class Secret:
            def __str__(self):
                raise AssertionError("must never format exception data")
            __repr__ = __str__
        namespace = {}
        exec(compile("def fixture():\n    raise ValueError('SYNTHETIC_SECRET_MESSAGE')\n",
                     str(Path(export.__file__).resolve()), "exec"), namespace)
        try:
            try:
                namespace["fixture"]()
            except ValueError as error:
                raise SystemExit(Secret()) from error
        except SystemExit as error:
            details = export.exception_details(error)
        encoded = json.dumps(details)
        self.assertEqual([entry["type"] for entry in details["chain"]],
                         ["builtins.SystemExit", "builtins.ValueError"])
        self.assertTrue(any(frame["function"] == "fixture" for frame in details["chain"][1]["frames"]))
        for forbidden in ("SYNTHETIC_SECRET_MESSAGE", "exit_code", "locals", "source", "message", str(export.ROOT)):
            self.assertNotIn(forbidden, encoded)
        class SpoofedExportError(export.ExportError):
            def __str__(self):
                raise AssertionError("subclass must never be formatted")
        self.assertEqual(export.bounded_reason(SpoofedExportError("export_timeout"), "fallback"), "fallback")
        self.assertEqual(export.bounded_reason(export.ExportError(Secret()), "fallback"), "fallback")
        self.assertEqual(export.bounded_reason(export.ExportError("unapproved_fixture"), "fallback"), "fallback")
        self.assertEqual(export.bounded_reason(export.ExportError("export_timeout"), "fallback"), "export_timeout")

    def test_worker_system_exit_writes_bounded_failure_not_payload(self):
        fake_torch = ModuleType("torch")
        model = ModuleType("executorch.examples.models.llama.model")
        model.Llama2Model = type("Llama2Model", (), {})
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            installed = output / "model.py"
            installed.write_text("# synthetic reviewed source\n")
            records = [{"path": export.MODEL_SOURCE, "installed_path": str(installed),
                        "effective_sha256": export.sha256(installed)}]
            with patch.object(export, "install_logging_guard"), \
                    patch.object(export, "verify_dependency_closure"), \
                    patch.dict(sys.modules, {"torch": fake_torch, "executorch.examples.models.llama.model": model}), \
                    patch("inspect.getsourcefile", return_value=str(installed)), \
                    patch("runpy.run_module", side_effect=SystemExit("SYNTHETIC_SECRET_EXIT")), \
                    patch.object(sys, "addaudithook"), patch.object(sys, "argv", ["fixture"]):
                result = export.worker_main([str(output), str(output), "{}", json.dumps(records)])
            report = json.loads((output / "worker-result.json").read_text())
            self.assertEqual(result, 1)
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["reason"], "export_entry_exited")
            self.assertEqual(report["error_details"]["chain"][0]["type"], "builtins.SystemExit")
            self.assertNotIn("SYNTHETIC_SECRET_EXIT", json.dumps(report))
            self.assertNotIn("exit_code", json.dumps(report))


class SourceAndInputTests(unittest.TestCase):
    def test_patch_removes_checkpoint_pickle_and_guards_other_loads(self):
        original = ("import torch\nclass Model:\n    def load(self):\n" +
                    export.CHECKPOINT_BLOCK + "        adapter = torch.load('adapter.pt')\n").encode()
        result = export.patched_source(export.MODEL_SOURCE, original, hashlib.sha256(original).hexdigest())
        self.assertNotIn(b"torch.load(", result)
        self.assertNotIn(b"torch.save(", result)
        self.assertIn(b"_qwen_reject_pickle('adapter.pt')", result)
        self.assertIn(b"checkpoint = _qwen_load_safetensors", result)

    def test_hash_and_context_drift_are_rejected(self):
        data = b"print('not upstream')\n"
        with self.assertRaisesRegex(export.ExportError, "hash_mismatch"):
            export.patched_source(export.MODEL_SOURCE, data, "0" * 64)
        with self.assertRaisesRegex(export.ExportError, "context_mismatch"):
            export.patched_source(export.MODEL_SOURCE, data, hashlib.sha256(data).hexdigest())

    def test_exporter_autodownload_call_is_removed(self):
        data = b"def export():\n        checkpoint = download_and_convert_hf_checkpoint(repo_id, convert_weights)\n"
        result = export.patched_source(export.EXPORT_SOURCE, data, hashlib.sha256(data).hexdigest())
        self.assertNotIn(b"download_and_convert_hf_checkpoint(", result)
        namespace = {}
        exec(result, namespace)
        with self.assertRaisesRegex(ValueError, "Explicit offline"):
            namespace["export"]()

    def test_artifact_hash_and_size_are_both_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "model.safetensors"
            path.write_bytes(b"sanitized not actual safetensors")
            entry = {"size_bytes": path.stat().st_size, "sha256": export.sha256(path)}
            export.verify_artifact(path, entry)
            path.write_bytes(b"changed")
            with self.assertRaises(export.ExportError):
                export.verify_artifact(path, entry)

    def test_paths_cannot_escape_artifacts_or_inject_hydra_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for value in ("../escape", "config/model.json", '.artifacts/${env:SECRET}',
                          '.artifacts/x",+model.use_lora=1'):
                with self.subTest(value=value), self.assertRaises((export.ExportError, export.CheckError)):
                    export.artifact_path(root, value)
            self.assertEqual(export.artifact_path(root, ".artifacts/model.safetensors"),
                             root / ".artifacts/model.safetensors")

    def test_lock_rejects_unpinned_unhashed_duplicate_and_wrong_required_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "requirements.lock"
            line = "torch==2.14.0 --hash=sha256:" + "a" * 64
            for text in ("torch>=2", "torch==2.14.0", line + "\n" + line):
                path.write_text(text)
                with self.assertRaises(export.ExportError):
                    export.read_dependency_lock(path, {"torch": "2.14.0"})
            path.write_text(line)
            self.assertEqual(export.read_dependency_lock(path, {"torch": "2.14.0"}), {"torch": "2.14.0"})
            with self.assertRaises(export.ExportError):
                export.read_dependency_lock(path, {"torch": "2.13.0"})

    def test_complete_manifest_rejects_omitted_transitive_and_changed_wheel_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "requirements.lock"
            expected = {"torch": {"version": "2.14.0", "sha256": "a" * 64},
                        "safetensors": {"version": "0.8.0", "sha256": "b" * 64}}
            path.write_text("torch==2.14.0 --hash=sha256:" + "a" * 64 + "\n")
            with self.assertRaisesRegex(export.ExportError, "incomplete"):
                export.read_dependency_lock(path, {"torch": "2.14.0"}, expected)
            path.write_text("torch==2.14.0 --hash=sha256:" + "c" * 64 + "\n")
            with self.assertRaisesRegex(export.ExportError, "manifest_mismatch"):
                export.read_dependency_lock(path, {"torch": "2.14.0"}, expected)

    def test_installed_dependency_closure_rejects_missing_or_extra_and_applies_markers(self):
        graph = {"a": ["b>=2", "absent; python_version < '2'"], "b": []}
        versions = {"a": "1", "b": "2"}
        kwargs = {"requires": graph.get, "version_of": versions.get, "parser": Requirement}
        self.assertEqual(export.verify_dependency_closure(versions, ["a"], **kwargs), ["a", "b"])
        with self.assertRaises(export.ExportError):
            export.verify_dependency_closure({"a": "1"}, ["a"], **kwargs)
        with self.assertRaises(export.ExportError):
            export.verify_dependency_closure({**versions, "unused": "3"}, ["a"], **kwargs)
        with self.assertRaises(export.ExportError):
            export.verify_dependency_closure({"a": "1", "b": "1"}, ["a"], **kwargs)

    def test_dependency_names_normalize_dots_underscores_and_hyphens(self):
        self.assertEqual(export.canonical_name("Ruamel.YAML"), "ruamel-yaml")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "requirements.lock"
            path.write_text("ruamel.yaml==1 --hash=sha256:" + "a" * 64 +
                            "\nruamel_yaml==1 --hash=sha256:" + "a" * 64)
            with self.assertRaises(export.ExportError):
                export.read_dependency_lock(path, {})

    def test_prepare_validates_both_files_before_mutation_and_can_repeat(self):
        model = ("import torch\nclass Model:\n    def load(self):\n" + export.CHECKPOINT_BLOCK).encode()
        library = b"def export():\n        checkpoint = download_and_convert_hf_checkpoint(repo_id, convert_weights)\n"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            sources = {export.MODEL_SOURCE: model, export.EXPORT_SOURCE: library}
            hashes = {name: hashlib.sha256(content).hexdigest() for name, content in sources.items()}
            for name, content in sources.items():
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(content)
            with patch.dict(export.SOURCE_HASHES, hashes, clear=True):
                (root / export.EXPORT_SOURCE).write_bytes(b"drift")
                with self.assertRaises(export.ExportError):
                    export.prepare_sources(root)
                self.assertEqual((root / export.MODEL_SOURCE).read_bytes(), model)
                (root / export.EXPORT_SOURCE).write_bytes(library)
                first = export.prepare_sources(root)
                self.assertEqual(export.prepare_sources(root), first)
                (root / (export.MODEL_SOURCE + ".qwen-original")).write_bytes(b"tampered backup")
                with self.assertRaises(export.ExportError):
                    export.prepare_sources(root)

    def test_interrupted_export_never_leaves_prepared_or_success_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "config").mkdir()
            artifact_root = root / ".artifacts"
            checkpoint = artifact_root / "models/model.safetensors"
            checkpoint.parent.mkdir(parents=True)
            checkpoint.write_bytes(b"synthetic fixture, not a model")
            weight = {"size_bytes": checkpoint.stat().st_size, "sha256": export.sha256(checkpoint)}
            lock = artifact_root / "venvs/qwen-export/requirements.lock"
            lock.parent.mkdir(parents=True)
            entries = [{"name": name, "version": version, "sha256": "a" * 64}
                       for name, version in export.PACKAGES.items()]
            lock.write_text("".join(f"{e['name']}=={e['version']} --hash=sha256:{e['sha256']}\n" for e in entries))
            python = lock.parent / ("Scripts/python.exe" if export.os.name == "nt" else "bin/python")
            python.parent.mkdir()
            python.write_bytes(b"never executed")
            baseline = {"runtime": {"revision": export.REVISION, "sources": [], "export_recipe": {},
                                     "host_package_candidates": entries,
                                     "dependency_resolution": {"lock_sha256": export.sha256(lock), "packages": entries}},
                        "models": [{"repo_id": export.MODEL_ID, "revision": "c1899de289a04d12100db370d81485cdf75e47ca",
                                    "weight_artifacts": [weight], "files": []}]}
            (root / "config/model-baselines.json").write_text(json.dumps(baseline))
            output = artifact_root / "exports/interrupted"
            args = SimpleNamespace(upstream_dir=artifact_root / "upstream" / ("executorch-" + export.REVISION),
                                   checkpoint=checkpoint, tokenizer_dir=checkpoint.parent,
                                   output_dir=output, execute=True)
            with patch.object(export, "install_logging_guard"), patch.object(export, "verify_checkout"), patch.object(export, "prepare_sources", return_value=[]), \
                    patch.object(export, "prepare_installed_sources", return_value=(artifact_root, [])), \
                    patch.object(export, "execute_export", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    export.run(args, root)
            report = json.loads((output / "export-provenance.json").read_text())
            self.assertEqual(report["status"], "interrupted")
            self.assertEqual(report["reason"], "export_cancelled")
            self.assertNotIn("pte_sha256", report)

    def test_wheel_adapter_verifies_crlf_origin_and_patches_only_isolated_install(self):
        model = ("import torch\nclass Model:\n    def load(self):\n" + export.CHECKPOINT_BLOCK).encode()
        library = b"def export():\n        checkpoint = download_and_convert_hf_checkpoint(repo_id, convert_weights)\n"
        originals = {export.MODEL_SOURCE: model, export.EXPORT_SOURCE: library}
        hashes = {name: hashlib.sha256(data).hexdigest() for name, data in originals.items()}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            venv = root / ".artifacts/venvs/qwen-export"
            wheelhouse = venv / "wheelhouse"
            wheelhouse.mkdir(parents=True)
            python = venv / ("Scripts/python.exe" if export.os.name == "nt" else "bin/python")
            site = venv / ("Lib/site-packages" if export.os.name == "nt" else "lib/python3.12/site-packages")
            wheel = wheelhouse / "executorch-1.5.1-fixture.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                for name, data in originals.items():
                    raw = data.replace(b"\n", b"\r\n")
                    archive.writestr("executorch/" + name, raw)
                    installed = site / "executorch" / name
                    installed.parent.mkdir(parents=True, exist_ok=True)
                    installed.write_bytes(raw)
            baseline = {"runtime": {"dependency_resolution": {"packages": [
                {"name": "executorch", "sha256": export.sha256(wheel)}]},
                "sources": [{"path": name, "sha256": digest} for name, digest in hashes.items()]}}
            with patch.dict(export.SOURCE_HASHES, hashes, clear=True):
                patches = [{"path": name, "adapted_sha256": hashlib.sha256(
                    export.patched_source(name, data, hashes[name])).hexdigest()}
                           for name, data in originals.items()]
                installed, records = export.prepare_installed_sources(root, python, baseline, patches)
                self.assertEqual(len(records), 2)
                for record in records:
                    self.assertEqual(export.sha256(Path(record["installed_path"])), record["effective_sha256"])
                    self.assertNotEqual(record["wheel_member_raw_sha256"], record["upstream_canonical_sha256"])
                self.assertEqual(export.prepare_installed_sources(root, python, baseline, patches)[1], records)
                (installed / export.MODEL_SOURCE).write_bytes(b"modified installed code")
                with self.assertRaisesRegex(export.ExportError, "installed_export_source_modified"):
                    export.prepare_installed_sources(root, python, baseline, patches)


if __name__ == "__main__":
    unittest.main()
