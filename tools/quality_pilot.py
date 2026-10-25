"""Fixed public Hungarian pilot; sanitized measurements, no answer payload logs."""
import hashlib
from decimal import Decimal
import json
from pathlib import Path
import sys
from tools import quality_reference as reference

CASE_IDS = ("G01", *(f"HU{i:02d}" for i in range(1, 13)))
CORPUS_SHA256 = "41d2fcf05095d1d28e9439f31afa6225dabb403b50567c12de75f68cc15f0dee"


def load_cases(root):
    path = reference.safe_path(root, reference.CORPUS)
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != CORPUS_SHA256:
        raise reference.CheckError("public_pilot_corpus_digest_mismatch")
    cases = data["cases"]
    if (data["schema_version"] != 1 or tuple(c["id"] for c in cases) != CASE_IDS or
            any(not isinstance(c["prompt"], str) or not 0 < len(c["prompt"].encode("utf-8")) <= 1024
                for c in cases)):
        raise reference.CheckError("public_pilot_fixture_mismatch")
    return cases


def render_case(case):
    return ("<|im_start|>user\n" + case["prompt"] + " /no_think<|im_end|>\n"
            "<|im_start|>assistant\n<think>\n\n</think>\n\n")


def deterministic_check(case, answer):
    if case["expected_kind"] == "review":
        return None
    if case["expected_kind"] == "exact":
        return answer.strip() == case["expected"]
    if case["expected_kind"] != "json":
        raise reference.CheckError("unsupported_pilot_predicate")
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate")
            value[key] = item
        return value
    def no_constant(_):
        raise ValueError("nonfinite")
    try:
        parsed = json.loads(answer, object_pairs_hook=unique, parse_constant=no_constant,
                            parse_float=Decimal, parse_int=Decimal)
        return (isinstance(parsed, dict) and set(parsed) == {"nev", "kor"} and
                type(parsed["nev"]) is str and type(parsed["kor"]) is Decimal and parsed["kor"].is_finite() and
                parsed == case["expected"])
    except (ValueError, TypeError):
        return False


def worker(output):
    reference.guards.install_logging_guard()
    result = {"status": "failed", "raw_answer_saved": False, "cases": [],
              "quality_gate": "not_accepted_qualitative_scores_pending"}
    try:
        directory, versions, hashes = reference.verified_inputs(reference.ROOT)
        reference.guards.verify_dependency_closure(versions, reference.guards.PACKAGES)
        if Path(sys.prefix).resolve() != (reference.ROOT / ".artifacts/venvs/qwen-export").resolve():
            raise reference.CheckError("unexpected_venv")
        cases = load_cases(reference.ROOT)
        sys.addaudithook(reference.guards.deny_export_event)
        import torch
        torch.load = reference.guards.forbidden_serialization
        torch.save = reference.guards.forbidden_serialization
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        from transformers import AutoTokenizer, GenerationConfig
        tokenizer = AutoTokenizer.from_pretrained(str(directory), local_files_only=True,
                                                  trust_remote_code=False, use_fast=True)
        model = reference.verified_float_model(directory, result)
        if any(parameter.dtype != torch.float32 for parameter in model.parameters()):
            raise reference.CheckError("float_dtype_mismatch")
        result["model_state"] = reference.model_state_fingerprint(model)
        result.update(model_revision=reference.MODEL_REVISION, checkpoint_sha256=hashes["model.safetensors"],
                      dtype="float32", do_sample=False, max_new_tokens=128, eos_token_ids=[151645],
                      cases_sha256=hashlib.sha256(json.dumps(cases, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest())
        for case in cases:
            prompt = render_case(case)
            ids = tokenizer.encode(prompt, add_special_tokens=False)
            inputs = torch.tensor([ids], dtype=torch.long)
            with torch.inference_mode():
                generated = model.generate(input_ids=inputs, attention_mask=torch.ones_like(inputs),
                    generation_config=GenerationConfig(do_sample=False, max_new_tokens=128,
                        eos_token_id=[151645], pad_token_id=151643, use_cache=True))
            new_ids = generated[0, len(ids):].tolist()
            decoded = tokenizer.decode(new_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
            answer = reference.re.split(r"<\|(?:im_end|endoftext)\|>", decoded, maxsplit=1)[0]
            result["cases"].append({"id": case["id"], "fixture_sha256": reference.text_digest(prompt),
                "input_token_ids_sha256": reference.token_digest(ids),
                **reference.summarize_answer(decoded, new_ids),
                "deterministic_match": deterministic_check(case, answer)})
        result["status"] = "observed"
        return 0
    except Exception as error:
        result.update(error_details=reference.guards.exception_details(error))
        return 1
    finally:
        reference.write_json(reference.safe_path(reference.ROOT, output / "worker-result.json"), result)
