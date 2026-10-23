import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import phone_benchmark as bench


def metrics():
    return dict(model_load_start_ms=10, model_load_end_ms=60,
                inference_start_ms=70, prompt_eval_end_ms=170,
                first_token_ms=180, inference_end_ms=370,
                prompt_tokens=12, generated_tokens=4)


def resource():
    return dict(exit_code=0, timed_out=False, interrupted=False,
                peak_rss_kib=123456, wall_ms=400)


class PhoneMeasurements(unittest.TestCase):
    def test_pinned_observer_definitions_and_no_prompt_persistence(self):
        observer = bench.Observer()
        payload = metrics() | {"prompt": "DO NOT PERSIST", "decoded_text": "SECRET OUTPUT"}
        wire = (b"secret raw generated output\nPyTorchObserver " + json.dumps(payload).encode()
                + b"\nP2PLLMResource " + json.dumps(resource()).encode() + b"\n")
        for offset in range(0, len(wire), 7):
            observer.feed(wire[offset:offset+7])
        result = observer.finish()
        self.assertEqual(result["load_ms"], 50)
        self.assertEqual(result["ttft_ms_excluding_load"], 110)
        self.assertEqual(result["runner_decode_tokens_per_second"], 20)
        self.assertNotIn("SECRET", json.dumps(observer.stats))
        self.assertEqual(result["peak_rss_kib"], 123456)

    def test_missing_inverted_nonfinite_or_boolean_metrics_rejected(self):
        bad = [metrics() | {"first_token_ms": -1}, metrics() | {"model_load_end_ms": 71},
               metrics() | {"inference_end_ms": float("nan")}, metrics() | {"prompt_tokens": True},
               metrics() | {"first_token_ms": 169}, metrics() | {"generated_tokens": 1.5},
               metrics() | {"first_token_ms": 10**400}]
        missing = metrics()
        del missing["first_token_ms"]
        for values in [*bad, missing]:
            with self.subTest(values=values), self.assertRaises(bench.MeasurementError):
                bench.derive(values, resource())

    def test_duplicate_records_and_keys_rejected(self):
        observer = bench.Observer()
        wire = b"PyTorchObserver " + json.dumps(metrics()).encode() + b"\n"
        observer.feed(wire)
        with self.assertRaises(bench.MeasurementError):
            observer.feed(wire)
        with self.assertRaises(bench.MeasurementError):
            bench.read_json('{"first_token_ms": 1, "first_token_ms": 2}')

    def test_output_and_line_caps_and_invalid_json(self):
        for data in [b"x" * 65537, b"x" * (2 * 1024 * 1024 + 1),
                     b'PyTorchObserver {broken}\n', b'PyTorchObserver []\n',
                     b'PyTorchObserver {"first_token_ms": NaN}\n']:
            with self.subTest(length=len(data)), self.assertRaises(bench.MeasurementError):
                bench.Observer().feed(data)

    def test_failure_timeout_and_unknown_memory_do_not_pass(self):
        for values in [resource() | {"exit_code": 137}, resource() | {"timed_out": True},
                       resource() | {"interrupted": True}, resource() | {"peak_rss_kib": 0},
                       resource() | {"wall_ms": float("inf")}]:
            with self.subTest(values=values), self.assertRaises(bench.MeasurementError):
                bench.derive(metrics(), values)

    def test_adb_selection_does_not_expose_serial_or_raw_errors(self):
        secret = "PRIVATE-DEVICE-ID"
        fake = subprocess.CompletedProcess([], 0, ("List of devices attached\n"+secret+"\tdevice\n").encode(), b"")
        with patch.object(bench.subprocess, "run", return_value=fake):
            adb = bench.Adb("fake-adb")
            self.assertEqual(adb.serial, secret)
        failed = subprocess.CompletedProcess([], 1, secret.encode(), b"private raw error")
        with patch.object(bench.subprocess, "run", return_value=failed), self.assertRaises(bench.MeasurementError) as error:
            bench.Adb("fake-adb")
        self.assertNotIn(secret, str(error.exception))

    def test_absent_unauthorized_and_multiple_devices_rejected(self):
        for state in ["", "private\tunauthorized\n", "a\tdevice\nb\tdevice\n"]:
            fake = subprocess.CompletedProcess([], 0, ("List of devices attached\n"+state).encode(), b"")
            with patch.dict(bench.os.environ, {}, clear=True), patch.object(bench.subprocess, "run", return_value=fake):
                with self.assertRaises(bench.MeasurementError):
                    bench.Adb("fake-adb")

    def test_unavailable_thermal_is_unknown_and_power_is_explicit(self):
        adb = object.__new__(bench.Adb)
        battery = 'temperature: 305\nstatus: 2\nUSB powered: true\nAC powered: false\n'
        with patch.object(adb, "shell", side_effect=[battery, bench.MeasurementError("Unavailable")]):
            data = adb.context()
        self.assertEqual(data["battery_temperature_c"], 30.5)
        self.assertIsNone(data["thermal_status"])
        self.assertTrue(data["power_connected"]["USB"])
        self.assertIsNone(data["power_connected"]["Wireless"])

    def test_recipe_pin_path_and_metadata_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"artifact"
            path.write_bytes(b"fixture bytes, not a model")
            artifacts = {key: dict(local_path=str(path), remote_path=bench.REMOTE+name,
                                  sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                         for key, name in [("launcher", "bench_exec"), ("runner", "llama_main"),
                                           ("model", "model.pte"), ("tokenizer", "tokenizer.json"),
                                           ("fixture", "fixture.txt")]}
            recipe = dict(schema_version=1, model_id="Qwen/Qwen3-0.6B", model_revision="a"*40,
                          runtime_revision="b"*40, quantization="8da4w", export_config_sha256="c"*64,
                          requested_backend="cpu-xnnpack", trials=3, max_new_tokens=32,
                          cpu_threads=2, timeout_seconds=300, artifacts=artifacts)
            target = Path(directory)/"recipe.json"
            def check(values):
                target.write_text(json.dumps(values), encoding="utf-8")
                return bench.load_recipe(target)
            self.assertEqual(check(recipe)["trials"], 3)
            for bad in [recipe | {"trials": 1}, recipe | {"model_revision": "main"},
                        recipe | {"prompt": "secret"}, recipe | {"timeout_seconds": True}]:
                with self.assertRaises(bench.MeasurementError):
                    check(bad)
            artifacts["model"]["remote_path"] = bench.REMOTE+"model.pte;reboot"
            with self.assertRaises(bench.MeasurementError):
                check(recipe)
            artifacts["model"]["remote_path"] = bench.REMOTE+"model.pte"
            artifacts["model"]["sha256"] = "d"*64
            with self.assertRaises(bench.MeasurementError):
                check(recipe)

    def test_output_confined_and_failed_probe_retained_without_raw_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(bench, "ROOT", root):
                with self.assertRaises(bench.MeasurementError):
                    bench.evidence_path("tracked-source.txt")
                output = root/".artifacts"/"no-phone.json"
                with patch.object(sys, "argv", ["phone_benchmark", "probe", "--output", str(output)]), \
                     patch.object(bench, "Adb", side_effect=bench.MeasurementError("No authorized phone")):
                    self.assertEqual(bench.main(), 2)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["status"], "blocked")
                self.assertEqual(report["run_kind"], "device_inventory")

    def test_missing_resource_never_infers_measured_success(self):
        observer = bench.Observer()
        observer.feed(b"PyTorchObserver "+json.dumps(metrics()).encode()+b"\n")
        with self.assertRaises(bench.MeasurementError):
            observer.finish()

    def test_failed_atomic_checkpoint_keeps_previous_envelope(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"report.json"
            path.write_text('{"status":"initial"}', encoding="utf-8")
            with patch.object(bench.os, "replace", side_effect=OSError("fixture")):
                with self.assertRaises(OSError):
                    bench.checkpoint(path, {"status": "new"})
            self.assertEqual(json.loads(path.read_text())["status"], "initial")
            self.assertEqual(len(list(path.parent.iterdir())), 1)

    def test_keyboard_interrupt_probe_keeps_sanitized_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root/".artifacts"/"cancelled.json"
            with patch.object(bench, "ROOT", root), \
                 patch.object(sys, "argv", ["phone_benchmark", "probe", "--output", str(output)]), \
                 patch.object(bench, "Adb", side_effect=KeyboardInterrupt):
                self.assertEqual(bench.main(), 2)
            self.assertEqual(json.loads(output.read_text())["status"], "interrupted")

    def test_adb_memtotal_accepts_crlf(self):
        adb = object.__new__(bench.Adb)
        with patch.object(adb, "shell", side_effect=["fixture\r\n"]*len(bench.PROPS)+["MemTotal: 123456 kB\r\n"]), \
             patch.object(adb, "context", return_value={}):
            self.assertEqual(adb.probe()["mem_total_kib"], 123456)

    def test_actual_host_process_is_reaped_when_wait_is_interrupted(self):
        recipe = {"timeout_seconds": 1, "max_new_tokens": 4, "cpu_threads": 1,
                  "artifacts": {k: {"remote_path": bench.REMOTE+k} for k in
                                ("launcher", "runner", "model", "tokenizer", "fixture")}}
        adb = SimpleNamespace(executable="unused", serial="not-recorded")
        original = subprocess.Popen
        children = []
        def launch(_args, **kwargs):
            child = original([sys.executable, "-c", "import time; time.sleep(20)"], **kwargs)
            wait = child.wait
            calls = 0
            def interrupt_once(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise KeyboardInterrupt
                return wait(*args, **kwargs)
            child.wait = interrupt_once
            children.append(child)
            return child
        with patch.object(bench.subprocess, "Popen", side_effect=launch):
            with self.assertRaises(KeyboardInterrupt):
                bench.collect_trial(adb, recipe)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)

    def test_actual_host_output_flood_is_stopped_and_reported(self):
        recipe = {"timeout_seconds": 1, "max_new_tokens": 4, "cpu_threads": 1,
                  "artifacts": {k: {"remote_path": bench.REMOTE+k} for k in
                                ("launcher", "runner", "model", "tokenizer", "fixture")}}
        adb = SimpleNamespace(executable="unused", serial="not-recorded")
        original = subprocess.Popen
        children = []
        def launch(_args, **kwargs):
            child = original([sys.executable, "-c", "import sys,time; sys.stdout.write('x'*100000); sys.stdout.flush(); time.sleep(20)"], **kwargs)
            children.append(child)
            return child
        with patch.object(bench.subprocess, "Popen", side_effect=launch):
            result = bench.collect_trial(adb, recipe)
        self.assertEqual(result["status"], "failed")
        self.assertIn("limit exceeded", result["error"])
        self.assertIsNotNone(children[0].poll())


if __name__ == "__main__":
    unittest.main()
