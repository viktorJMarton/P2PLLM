"""Offline pinned FLOAT G01 diagnosis; never persist prompts, answers or tensors.

Only the reviewed public G01 fixture is accepted. This does not export a model.
Python logging is guarded before model imports; child console output is discarded.
These protections are not a native-code or OS confidentiality sandbox.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_qwen as guards
from tools.run_checks import CheckError, WindowsJob, safe_path, utc_now, write_json

MODEL_REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
MODEL_DIR = ".artifacts/models/Qwen3-0.6B-" + MODEL_REVISION
CORPUS = "tests/fixtures/local-inference-quality.json"
FIXTURE_ID = "G01"
PUBLIC_GREETING = "Hogy vagy?"
EOS_ID = 151645  # pinned export YAML, not the HF generation_config defaults
MAX_NEW_TOKENS = 128


def text_digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def token_digest(ids):
    return text_digest(json.dumps(ids, separators=(",", ":")))


def verified_float_model(directory, result):
    """Reject partially initialized reference models; persist counts, never keys."""
    from transformers import AutoModelForCausalLM

    model, info = AutoModelForCausalLM.from_pretrained(
        str(directory), local_files_only=True, trust_remote_code=False,
        use_safetensors=True, dtype="float32", attn_implementation="eager",
        output_loading_info=True,
    )
    fields = ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")
    if not isinstance(info, dict) or any(
        key not in info or not isinstance(info[key], (list, tuple, set)) for key in fields
    ):
        raise CheckError("invalid_float_loading_receipt")
    counts = {key: len(info[key]) for key in fields}
    result["loading_counts"] = counts
    if any(counts.values()):
        raise CheckError("incomplete_float_checkpoint_load")
    model.eval()
    return model


def model_state_fingerprint(model):
    """Hash parameters and all buffers, including nonpersistent rotary buffers.

    Called only on the CPU FP32 reference. memoryview avoids serializing tensor
    payloads to files or copying an entire parameter into a Python bytes object.
    """
    digest = hashlib.sha256()
    count, size = 0, 0
    tensors = [("parameter:" + name, value) for name, value in model.named_parameters()]
    tensors += [("buffer:" + name, value) for name, value in model.named_buffers()]
    for name, value in sorted(tensors, key=lambda item: item[0]):
        if value.device.type != "cpu" or value.is_meta:
            raise CheckError("unsupported_reference_state_device")
        array = value.detach().contiguous().numpy()
        metadata = json.dumps([name, str(value.dtype), list(value.shape)], separators=(",", ":")).encode()
        digest.update(len(metadata).to_bytes(8, "big"))
        digest.update(metadata)
        raw = memoryview(array).cast("B")
        digest.update(raw)
        count += 1
        size += raw.nbytes
    return {"format": "named-parameters-and-all-buffers-v1", "sha256": digest.hexdigest(),
            "tensor_count": count, "tensor_bytes": size}


def rendered_greeting(root):
    corpus_path = safe_path(root, CORPUS)
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    matches = [case for case in corpus["cases"] if case["id"] == FIXTURE_ID]
    if corpus["schema_version"] != 1 or len(matches) != 1 or matches[0]["prompt"] != PUBLIC_GREETING:
        raise CheckError("public_fixture_mismatch")
    return ("<|im_start|>user\n" + PUBLIC_GREETING + " /no_think<|im_end|>\n"
            "<|im_start|>assistant\n<think>\n\n</think>\n\n")


def summarize_answer(decoded, ids):
    # Same known-EOS removal as JNI; retain distinct raw and trimmed digests.
    text = re.split(r"<\|(?:im_end|endoftext)\|>", decoded, maxsplit=1)[0]
    trimmed = text.strip()
    words = re.findall(r"\w+", trimmed.casefold())
    counts = Counter(tuple(words[i:i + 3]) for i in range(max(0, len(words) - 2)))
    repeated = max(counts.values(), default=0)
    eos = bool(ids and ids[-1] == EOS_ID)
    return {"answer_raw_bytes": len(text.encode("utf-8")), "answer_raw_sha256": text_digest(text),
            "answer_bytes": len(trimmed.encode("utf-8")), "answer_sha256": text_digest(trimmed),
            "generated_tokens": len(ids), "generated_token_ids_sha256": token_digest(ids),
            "eos_seen": eos, "stop_reason": "eos" if eos else "token_budget" if len(ids) == MAX_NEW_TOKENS else "unexpected",
            "max_repeated_word_trigram": repeated, "pathological_repetition_flag": repeated >= 3,
            "directive_fragment_flag": bool(re.search(r"/no(?:_think)?\b", trimmed, re.I)),
            "coherence_score": "not_human_rated", "raw_answer_saved": False}


def verified_inputs(root):
    baseline = json.loads(safe_path(root, "config/model-baselines.json").read_text(encoding="utf-8"))
    model = next(m for m in baseline["models"] if m["repo_id"] == guards.MODEL_ID)
    if model["revision"] != MODEL_REVISION or baseline["runtime"]["revision"] != guards.REVISION:
        raise CheckError("revision_mismatch")
    directory = safe_path(root, MODEL_DIR)
    entries = model["files"] + model["weight_artifacts"]
    if len(model["weight_artifacts"]) != 1 or model["weight_artifacts"][0]["path"] != "model.safetensors":
        raise CheckError("safetensors_checkpoint_required")
    for entry in entries:
        guards.verify_artifact(safe_path(root, directory / entry["path"]), entry)
    resolution = baseline["runtime"]["dependency_resolution"]
    lock = safe_path(root, ".artifacts/venvs/qwen-export/requirements.lock")
    if guards.sha256(lock) != resolution["lock_sha256"]:
        raise CheckError("dependency_lock_mismatch")
    versions = guards.read_dependency_lock(lock, guards.PACKAGES, {p["name"]: p for p in resolution["packages"]})
    return directory, versions, {entry["path"]: entry["sha256"] for entry in entries}


def worker(output):
    guards.install_logging_guard()  # before torch/transformers/tokenizer imports
    result = {"status": "failed", "phase": "preconditions", "raw_answer_saved": False}
    try:
        output = safe_path(ROOT, output)
        directory, versions, artifact_hashes = verified_inputs(ROOT)
        if Path(sys.prefix).resolve() != (ROOT / ".artifacts/venvs/qwen-export").resolve():
            raise CheckError("unexpected_venv")
        guards.verify_dependency_closure(versions, guards.PACKAGES)
        prompt = rendered_greeting(ROOT)
        result.update(fixture_id=FIXTURE_ID, fixture_sha256=text_digest(prompt), artifact_sha256=artifact_hashes,
                      package_versions=versions, model_revision=MODEL_REVISION, dtype="float32",
                      attention_implementation="eager", device="cpu", cpu_threads=4,
                      max_new_tokens=MAX_NEW_TOKENS, temperature=0, do_sample=False,
                      eos_token_ids=[EOS_ID], pad_token_id=151643, num_bos=0, num_eos=0,
                      token_id_hash_format="compact-json-array-utf8-v1", phone_token_id_parity="not_measured")
        sys.addaudithook(guards.deny_export_event)
        result["phase"] = "torch_import"
        import torch
        torch.load = guards.forbidden_serialization
        torch.save = guards.forbidden_serialization
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        torch.manual_seed(0)
        result["phase"] = "tokenizer"
        from transformers import AutoTokenizer, GenerationConfig
        tokenizer = AutoTokenizer.from_pretrained(str(directory), local_files_only=True,
                                                  trust_remote_code=False, use_fast=True)
        ids = tokenizer.encode(prompt, add_special_tokens=False)
        result.update(input_tokens=len(ids), input_token_ids_sha256=token_digest(ids))
        from pytorch_tokenizers import CppHFTokenizer
        native_tokenizer = CppHFTokenizer()
        native_tokenizer.load(str(directory / "tokenizer.json"))
        native_ids = native_tokenizer.encode(prompt, 0, 0)
        result.update(host_cpp_input_token_ids_sha256=token_digest(native_ids),
                      host_hf_cpp_token_ids_equal=ids == native_ids)
        if ids != native_ids:
            raise CheckError("host_tokenizer_mismatch")
        result["phase"] = "float_model_load"
        start = time.monotonic()
        model = verified_float_model(directory, result)
        if any(parameter.dtype != torch.float32 for parameter in model.parameters()):
            raise CheckError("float_dtype_mismatch")
        result["load_seconds"] = round(time.monotonic() - start, 3)
        result["model_state"] = model_state_fingerprint(model)
        result["phase"] = "generation"
        config = GenerationConfig(do_sample=False, max_new_tokens=MAX_NEW_TOKENS,
                                  eos_token_id=[EOS_ID], pad_token_id=151643, use_cache=True)
        inputs = torch.tensor([ids], dtype=torch.long)
        start = time.monotonic()
        with torch.inference_mode():
            generated = model.generate(input_ids=inputs, attention_mask=torch.ones_like(inputs), generation_config=config)
        new_ids = generated[0, len(ids):].tolist()
        result["generation_seconds"] = round(time.monotonic() - start, 3)
        if len(new_ids) > MAX_NEW_TOKENS:
            raise CheckError("generation_bound_exceeded")
        result.update(summarize_answer(tokenizer.decode(new_ids, skip_special_tokens=False,
                                                      clean_up_tokenization_spaces=False), new_ids))
        result.update(status="observed", phase="complete")
        return 0
    except Exception as error:
        result.update(reason="reference_worker_failed", error_details=guards.exception_details(error))
        return 1
    finally:
        write_json(safe_path(ROOT, output / "worker-result.json"), result)


def run(output, timeout=600, pilot=False):
    output = safe_path(ROOT, output)
    if not output.is_relative_to(ROOT / ".artifacts") or output.exists():
        raise CheckError("new_artifacts_output_required")
    output.mkdir(parents=True)
    report = {"schema_version": 1, "work_id": "WORK-0002", "run_kind": "pinned_float_G01_reference",
              "started_at": utc_now(), "status": "failed", "raw_answer_saved": False,
              "scope": "G01 synthetic diagnostic; no general quality/numerical equivalence claim"}
    if pilot:
        from tools.quality_pilot import load_cases, CORPUS_SHA256
        load_cases(ROOT)
        report.update(run_kind="pinned_float_public_pilot",
                      scope="13 fixed public cases; qualitative scoring pending, not acceptance",
                      pilot_harness_sha256=guards.sha256(ROOT / "tools/quality_pilot.py"),
                      public_corpus_sha256=CORPUS_SHA256)
    process = job = None
    try:
        _, _, hashes = verified_inputs(ROOT)
        report.update(fixture_sha256=text_digest(rendered_greeting(ROOT)), artifact_sha256=hashes,
                      harness_sha256=guards.sha256(Path(__file__)))
        python = safe_path(ROOT, ".artifacts/venvs/qwen-export/Scripts/python.exe")
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
        env.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1",
                   PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", TOKENIZERS_PARALLELISM="false")
        job = WindowsJob() if os.name == "nt" else None
        with open(os.devnull, "wb") as discarded:
            command = [str(python), "-I", str(Path(__file__)), "--worker", str(output)]
            if pilot:
                command.append("--pilot")
            process = subprocess.Popen(command,
                cwd=ROOT, env=env, stdout=discarded, stderr=discarded, start_new_session=os.name != "nt")
            if job:
                job.assign(process)
            report["worker_exit_code"] = process.wait(timeout=timeout)
        worker_report = json.loads(safe_path(ROOT, output / "worker-result.json").read_text(encoding="utf-8"))
        report["result"] = worker_report
        if report["worker_exit_code"] == 0 and worker_report["status"] == "observed":
            report["status"] = "observed"
    except subprocess.TimeoutExpired:
        report["reason"] = "reference_timeout"
    except Exception as error:
        report.update(reason="reference_precondition_or_process_failed", error_details=guards.exception_details(error))
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
        report["finished_at"] = utc_now()
        write_json(output / "report.json", report)
    return 0 if report["status"] == "observed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--pilot", action="store_true", help="Run the fixed13-case public pilot")
    args = parser.parse_args()
    if args.worker:
        if args.pilot:
            from tools.quality_pilot import worker as pilot_worker
            raise SystemExit(pilot_worker(Path(args.worker)))
        raise SystemExit(worker(Path(args.worker)))
    if not args.output:
        parser.error("--output is required")
    try:
        raise SystemExit(run(args.output, pilot=args.pilot))
    except CheckError:
        print("reference_output_precondition_failed", file=sys.stderr)
        raise SystemExit(1)
