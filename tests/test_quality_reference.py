"""Sanitized pure boundaries; no model, torch, network or native library loading."""
import json
from array import array
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from types import ModuleType, SimpleNamespace
from tools import quality_reference as reference


class ReferenceBoundaryTests(unittest.TestCase):
    def test_state_fingerprint_includes_nonpersistent_buffers_without_payloads(self):
        class Tensor:
            device = SimpleNamespace(type="cpu")
            is_meta = False
            dtype = "float32"
            shape = (2,)

            def __init__(self, numbers):
                self.data = array("f", numbers)

            def detach(self):
                return self

            def contiguous(self):
                return self

            def numpy(self):
                return self.data

        parameter, buffer = Tensor([1, 2]), Tensor([3, 4])
        model = SimpleNamespace(
            named_parameters=lambda: [("SYNTHETIC_CANARY", parameter)],
            named_buffers=lambda: [("rotary", buffer)],
        )
        first = reference.model_state_fingerprint(model)
        self.assertEqual(first["tensor_count"], 2)
        self.assertEqual(first["tensor_bytes"], 16)
        self.assertNotIn("CANARY", json.dumps(first))
        self.assertEqual(first, reference.model_state_fingerprint(model))
        buffer.data[0] = 5
        self.assertNotEqual(first["sha256"], reference.model_state_fingerprint(model)["sha256"])

    def test_float_loading_requires_complete_receipt_without_key_payloads(self):
        module = ModuleType("transformers")
        module.AutoModelForCausalLM = MagicMock()
        model = MagicMock()
        fields = ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")
        for failing in (None, *fields):
            info = {field: [] for field in fields}
            if failing:
                info[failing] = ["SYNTHETIC_PRIVATE_CANARY"]
            module.AutoModelForCausalLM.from_pretrained.return_value = model, info
            result = {}
            with patch.dict("sys.modules", {"transformers": module}):
                if failing:
                    with self.assertRaisesRegex(reference.CheckError, "incomplete_float_checkpoint_load"):
                        reference.verified_float_model(Path("synthetic"), result)
                else:
                    self.assertIs(reference.verified_float_model(Path("synthetic"), result), model)
            self.assertNotIn("CANARY", json.dumps(result))
            self.assertEqual(sum(result["loading_counts"].values()), int(failing is not None))
        self.assertTrue(module.AutoModelForCausalLM.from_pretrained.call_args.kwargs["output_loading_info"])
        for info in ({}, {field: None for field in fields}):
            module.AutoModelForCausalLM.from_pretrained.return_value = model, info
            with patch.dict("sys.modules", {"transformers": module}):
                with self.assertRaisesRegex(reference.CheckError, "invalid_float_loading_receipt"):
                    reference.verified_float_model(Path("synthetic"), {})

    def test_exact_current_template_matches_observed_phone_fixture(self):
        rendered = reference.rendered_greeting(reference.ROOT)
        self.assertEqual(reference.text_digest(rendered), "9c66202adeabb9f681c819d21ae1d0aec575090b40961daeaf6efd38495dca9d")
        self.assertIn(" /no_think<|im_end|>", rendered)

    def test_rejects_nonpublic_or_duplicate_greeting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / reference.CORPUS
            path.parent.mkdir(parents=True)
            for cases in ([{"id": "G01", "prompt": "unapproved text"}],
                          [{"id": "G01", "prompt": reference.PUBLIC_GREETING}] * 2):
                path.write_text(json.dumps({"schema_version": 1, "cases": cases}), encoding="utf-8")
                with self.assertRaises(reference.CheckError):
                    reference.rendered_greeting(root)

    def test_repetition_and_directive_flags_without_payload_serialization(self):
        text = ("synthetic payload canary " * 4) + "/No"
        report = reference.summarize_answer(text, [2] * 128)
        self.assertTrue(report["pathological_repetition_flag"])
        self.assertTrue(report["directive_fragment_flag"])
        self.assertEqual(report["stop_reason"], "token_budget")
        self.assertNotIn("canary", json.dumps(report))
        self.assertFalse(report["raw_answer_saved"])

    def test_eos_trim_and_stop_reason_are_separate_observations(self):
        report = reference.summarize_answer("  synthetic answer \n<|im_end|>", [42, reference.EOS_ID])
        self.assertEqual(report["answer_raw_sha256"], reference.text_digest("  synthetic answer \n"))
        self.assertEqual(report["answer_sha256"], reference.text_digest("synthetic answer"))
        self.assertEqual(report["stop_reason"], "eos")
        self.assertFalse(report["pathological_repetition_flag"])
        self.assertEqual(reference.summarize_answer("x", [2])["stop_reason"], "unexpected")

    def test_token_hash_uses_pinned_serialization(self):
        self.assertEqual(reference.token_digest([1, 20]), reference.text_digest("[1,20]"))
        self.assertNotEqual(reference.token_digest([1, 20]), reference.token_digest([12, 0]))

    def test_launcher_discards_console_and_records_worker_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / ".artifacts/reference"
            process = MagicMock()
            process.wait.return_value = 0
            process.poll.return_value = 0

            def start(*args, **kwargs):
                self.assertEqual(kwargs["stdout"], kwargs["stderr"])
                self.assertEqual(kwargs["env"]["HF_HUB_OFFLINE"], "1")
                self.assertEqual(kwargs["env"]["TRANSFORMERS_OFFLINE"], "1")
                self.assertIn("-I", args[0])
                (output / "worker-result.json").write_text('{"status":"observed"}', encoding="utf-8")
                return process

            with patch.object(reference, "ROOT", root), \
                 patch.object(reference, "verified_inputs", return_value=(root, {}, {})), \
                 patch.object(reference, "rendered_greeting", return_value="synthetic public fixture"), \
                 patch.object(reference.subprocess, "Popen", side_effect=start), \
                 patch.object(reference, "WindowsJob"):
                self.assertEqual(reference.run(output), 0)
            report = json.loads((output / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "observed")
            self.assertEqual(report["worker_exit_code"], 0)
            self.assertFalse(report["raw_answer_saved"])


if __name__ == "__main__":
    unittest.main()
