"""Collect pinned ExecuTorch phone trials; never persist raw model output/serials.

Tooling/fixture checks are not phone measurements. Unknown backend placement
keeps acceptance incomplete even when numeric observations are available.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import threading

try:
    from run_checks import safe_path
except ModuleNotFoundError:
    from tools.run_checks import safe_path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "/data/local/tmp/p2pllm-benchmark/"
STATS = ("model_load_start_ms", "model_load_end_ms", "inference_start_ms",
         "inference_end_ms", "prompt_eval_end_ms", "first_token_ms",
         "prompt_tokens", "generated_tokens")
PROPS = ("ro.product.manufacturer", "ro.product.model", "ro.product.device",
         "ro.build.version.release", "ro.build.version.sdk", "ro.build.display.id",
         "ro.product.cpu.abilist", "ro.soc.manufacturer", "ro.soc.model")


class MeasurementError(ValueError):
    pass


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite(value, name, positive=False):
    if (type(value) not in (float, int) or value < 0 or value > 10**18
            or not math.isfinite(value) or (positive and value == 0)):
        raise MeasurementError(f"Invalid numeric metric: {name}")
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise MeasurementError("Duplicate metric key")
        result[key] = value
    return result


def read_json(value):
    try:
        return json.loads(value, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise MeasurementError("Invalid structured measurement") from error


def derive(stats, resource):
    if not isinstance(stats, dict) or not isinstance(resource, dict):
        raise MeasurementError("Missing observer/resource record")
    for key in STATS:
        if key not in stats:
            raise MeasurementError(f"Missing observer field: {key}")
        finite(stats[key], key)
    for key in ("prompt_tokens", "generated_tokens"):
        if type(stats[key]) is not int or stats[key] <= 0:
            raise MeasurementError("Token counts must be positive integers")
    a, b = stats["model_load_start_ms"], stats["model_load_end_ms"]
    start, prefill, first, end = (stats[k] for k in
        ("inference_start_ms", "prompt_eval_end_ms", "first_token_ms", "inference_end_ms"))
    if not (a <= b <= start <= prefill <= first <= end) or end <= prefill:
        raise MeasurementError("Inconsistent observer timestamps")
    if type(resource.get("exit_code")) is not int or resource["exit_code"] != 0:
        raise MeasurementError("Runner failed")
    if resource.get("timed_out") is not False or resource.get("interrupted") is not False:
        raise MeasurementError("Runner timed out or was interrupted")
    memory = finite(resource.get("peak_rss_kib"), "peak_rss_kib", positive=True)
    wall = finite(resource.get("wall_ms"), "wall_ms", positive=True)
    return {"load_ms": b - a, "ttft_ms_excluding_load": first - start,
            "runner_decode_tokens_per_second": stats["generated_tokens"] * 1000 / (end - prefill),
            "observer_clock": "pinned runner CLOCK_REALTIME milliseconds; not monotonic",
            "token_count_semantics": "decode-loop tokens; excludes prefill first token; includes loop EOS",
            "ttft_endpoint": "runner first-token timestamp before tokenizer decode/callback; not host arrival",
            "peak_rss_kib": memory, "memory_method": "Android wait4 child ru_maxrss; KiB",
            "launcher_wall_ms": wall}


class Observer:
    """Discard all non-allowlisted output; bound stream and line bytes."""
    def __init__(self):
        self.stats = self.resource = None
        self.total = 0
        self.buffer = b""

    def feed(self, chunk):
        self.total += len(chunk)
        if self.total > 2 * 1024 * 1024:
            raise MeasurementError("Runner output limit exceeded")
        self.buffer += chunk
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            self.line(line)
        if len(self.buffer) > 65536:
            raise MeasurementError("Runner line limit exceeded")

    def line(self, raw):
        if len(raw) > 65536:
            raise MeasurementError("Runner line limit exceeded")
        for prefix, attribute in ((b"PyTorchObserver ", "stats"), (b"P2PLLMResource ", "resource")):
            if raw.startswith(prefix):
                if getattr(self, attribute) is not None:
                    raise MeasurementError("Duplicate observer/resource record")
                try:
                    data = read_json(raw[len(prefix):].decode("utf-8"))
                except UnicodeError as error:
                    raise MeasurementError("Invalid measurement encoding") from error
                if not isinstance(data, dict):
                    raise MeasurementError("Expected measurement object")
                allowed = STATS if attribute == "stats" else (
                    "exit_code", "timed_out", "interrupted", "peak_rss_kib", "wall_ms")
                cleaned = {k: data[k] for k in allowed if k in data}
                for key, value in cleaned.items():
                    if key in ("timed_out", "interrupted"):
                        if type(value) is not bool:
                            raise MeasurementError("Resource flags must be boolean")
                    else:
                        finite(value, key)
                setattr(self, attribute, cleaned)

    def finish(self):
        if self.buffer:
            self.line(self.buffer)
            self.buffer = b""
        return derive(self.stats, self.resource)


class Adb:
    def __init__(self, executable):
        self.executable = str(executable)
        listing = self.call(["devices"])
        devices = [parts[0] for line in listing.splitlines()[1:]
                   if len(parts := line.split()) == 2 and parts[1] == "device"]
        selected = os.environ.get("ANDROID_SERIAL")
        if selected:
            devices = [item for item in devices if item == selected]
        if len(devices) != 1:
            raise MeasurementError("Exactly one authorized phone required; connect/unlock/authorize USB debugging")
        self.serial = devices[0]  # In memory only; never serialized or printed.

    def call(self, args, timeout=30):
        try:
            result = subprocess.run([self.executable, *args], capture_output=True,
                                    timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise MeasurementError("ADB unavailable or timed out") from error
        if result.returncode:
            raise MeasurementError("ADB operation failed; raw diagnostics suppressed")
        if len(result.stdout) > 256 * 1024:
            raise MeasurementError("ADB metadata limit exceeded")
        return result.stdout.decode("utf-8", errors="replace")

    def shell(self, command):
        return self.call(["-s", self.serial, "shell", command])

    def context(self):
        def optional(command):
            try:
                return self.shell(command)
            except MeasurementError:
                return ""
        battery = optional("dumpsys battery")
        temp = re.search(r"^\s*temperature:\s*(-?\d+)\s*$", battery, re.M)
        thermal = optional("dumpsys thermalservice")
        status = re.search(r"^\s*Thermal Status:\s*(\d+)\s*$", thermal, re.M)
        charging = re.search(r"^\s*status:\s*(\d+)\s*$", battery, re.M)
        plugged = {key: (m[1] == "true") if (m := re.search(
            r"^\s*" + key + r" powered:\s*(true|false)\s*$", battery, re.M)) else None
                   for key in ("AC", "USB", "Wireless")}
        return {"battery_temperature_c": int(temp[1]) / 10 if temp else None,
                "thermal_status": int(status[1]) if status else None,
                "battery_status_code": int(charging[1]) if charging else None,
                "power_connected": plugged}

    def probe(self):
        device = {name: self.shell("getprop " + name).strip() for name in PROPS}
        ram = re.search(r"^MemTotal:\s*(\d+) kB\s*$", self.shell("cat /proc/meminfo"), re.M)
        device["mem_total_kib"] = int(ram[1]) if ram else None
        device["context"] = self.context()
        return device


def load_recipe(path):
    recipe = read_json(Path(path).read_text(encoding="utf-8"))
    if not isinstance(recipe, dict) or recipe.get("schema_version") != 1:
        raise MeasurementError("Unsupported recipe")
    allowed = {"schema_version", "model_id", "model_revision", "runtime_revision",
               "quantization", "export_config_sha256", "requested_backend", "trials",
               "max_new_tokens", "cpu_threads", "timeout_seconds", "artifacts"}
    if set(recipe) != allowed:
        raise MeasurementError("Recipe fields must match the allowlist; no prompt/output/custom metadata")
    for key in ("model_id", "model_revision", "runtime_revision", "quantization",
                "export_config_sha256", "requested_backend"):
        value = recipe.get(key)
        if not isinstance(value, str) or not value or len(value) > 200:
            raise MeasurementError(f"Missing recipe provenance: {key}")
    for key, length in (("model_revision", 40), ("runtime_revision", 40), ("export_config_sha256", 64)):
        if not re.fullmatch(r"[0-9a-f]{" + str(length) + "}", recipe[key]):
            raise MeasurementError(f"Immutable hash required: {key}")
    for key in ("trials", "max_new_tokens", "cpu_threads", "timeout_seconds"):
        if type(recipe.get(key)) is not int:
            raise MeasurementError(f"Integer required: {key}")
    if not (3 <= recipe["trials"] <= 10 and 2 <= recipe["max_new_tokens"] <= 512
            and 1 <= recipe["cpu_threads"] <= 16 and 1 <= recipe["timeout_seconds"] <= 1800):
        raise MeasurementError("Recipe bounds invalid")
    artifacts = recipe.get("artifacts", {})
    if not isinstance(artifacts, dict) or set(artifacts) != {"launcher", "runner", "model", "tokenizer", "fixture"}:
        raise MeasurementError("Exact five artifact roles required")
    for key, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            raise MeasurementError("Invalid artifact")
        if set(artifact) != {"local_path", "remote_path", "sha256"}:
            raise MeasurementError("Unexpected artifact metadata")
        remote = artifact.get("remote_path", "")
        if not re.fullmatch(re.escape(REMOTE) + r"[A-Za-z0-9_.-]+", remote) or remote.rsplit("/", 1)[-1] in (".", ".."):
            raise MeasurementError("Artifact must use safe benchmark directory path")
        expected = artifact.get("sha256", "")
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise MeasurementError("Artifact SHA256 required")
        local = Path(artifact.get("local_path", ""))
        if not local.is_file() or sha256(local) != expected:
            raise MeasurementError(f"Missing or changed local artifact: {key}")
    if not artifacts["model"]["remote_path"].endswith(".pte"):
        raise MeasurementError("Only reviewed ExecuTorch .pte models accepted")
    if len({a['remote_path'] for a in artifacts.values()}) != 5:
        raise MeasurementError("Artifact paths must be distinct")
    return recipe


def collect_trial(adb, recipe):
    artifacts = recipe["artifacts"]
    runner = [artifacts["launcher"]["remote_path"], str(recipe["timeout_seconds"]),
              artifacts["runner"]["remote_path"], "--model_path=" + artifacts["model"]["remote_path"],
              "--tokenizer_path=" + artifacts["tokenizer"]["remote_path"],
              "--prompt_file=" + artifacts["fixture"]["remote_path"], "--temperature=0",
              "--max_new_tokens=" + str(recipe["max_new_tokens"]),
              "--cpu_threads=" + str(recipe["cpu_threads"]), "--warmup=false", "--num_bos=0", "--num_eos=0"]
    observer = Observer()
    errors = []
    try:
        process = subprocess.Popen([adb.executable, "-s", adb.serial, "shell", shlex.join(runner)],
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError as error:
        raise MeasurementError("Could not start ADB runner") from error
    def consume():
        try:
            while block := process.stdout.read(4096):
                observer.feed(block)
        except (MeasurementError, OSError) as error:
            errors.append(str(error))
            process.kill()
    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    try:
        try:
            code = process.wait(timeout=recipe["timeout_seconds"] + 15)
        except subprocess.TimeoutExpired:
            errors.append("Host timeout; remote launcher retains its own bounded timeout")
            code = None
    finally:
        # Also runs on Ctrl-C: close our host connection, never kill adb globally.
        # Native supervisor catches HUP/PIPE and owns the bounded remote cleanup.
        if process.poll() is None:
            process.kill()
        process.wait(timeout=10)
        thread.join(timeout=5)
        if not thread.is_alive():
            process.stdout.close()
    if thread.is_alive():
        raise MeasurementError("ADB output did not close; last checkpoint retained")
    result = {"observer": observer.stats, "resource": observer.resource,
              "adb_exit_code": code, "status": "failed"}
    try:
        if errors:
            raise MeasurementError(errors[0])
        if code != 0:
            raise MeasurementError("ADB runner command failed")
        result["metrics"] = observer.finish()
        result["observer"], result["resource"] = observer.stats, observer.resource
        result["status"] = "observed"
    except MeasurementError as error:
        result["error"] = str(error)
    return result


def build_helper(output):
    try:
        from dev_env import configuration, environment
    except ModuleNotFoundError:
        from tools.dev_env import configuration, environment
    env = environment(ROOT / ".artifacts/toolchains", configuration())
    toolchain = Path(env["ANDROID_NDK_HOME"]) / "toolchains/llvm/prebuilt/windows-x86_64"
    output = evidence_path(output)
    if output.exists():
        raise MeasurementError("Helper output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [str(toolchain / "bin/clang.exe"), "--target=aarch64-linux-android26",
               "--sysroot=" + str(toolchain / "sysroot"), "-O2", "-Wall", "-Wextra", "-Werror",
               str(ROOT / "tools/android/bench_exec.c"), "-o", str(output)]
    subprocess.run(command, check=True, timeout=120)
    print(json.dumps({"helper_sha256": sha256(output), "target": "aarch64-linux-android26",
                      "scope": "cross-compiled; device execution not inferred"}))


def evidence_path(value):
    path = safe_path(ROOT, value)
    if not path.is_relative_to(ROOT / ".artifacts"):
        raise MeasurementError("Evidence/build outputs must be below .artifacts")
    return path


def checkpoint(output, report):
    # Serialize before replacement; interrupted writes preserve the last complete
    # envelope. Temporary files contain only the same allowlisted metadata.
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=output.parent, prefix=output.name+".",
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default=str(ROOT / ".artifacts/toolchains/android-sdk/platform-tools/adb.exe"))
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("probe").add_argument("--output", required=True)
    build = sub.add_parser("build-helper")
    build.add_argument("--output", required=True)
    run = sub.add_parser("run")
    run.add_argument("--recipe", required=True)
    run.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.action == "build-helper":
            build_helper(args.output)
            return 0
        output = evidence_path(args.output)
        if output.exists():
            raise MeasurementError("Evidence output already exists")
        output.parent.mkdir(parents=True, exist_ok=True)
        report = {"schema_version": 1, "work_id": "WORK-0002",
                  "run_kind": "device_inventory" if args.action == "probe" else "phone_inference",
                  "time_utc": datetime.now(timezone.utc).isoformat(), "status": "blocked"}
        # Exclusive creation means even failed/no-device attempts are retained.
        with output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        try:
            try:
                recipe = load_recipe(args.recipe) if args.action == "run" else None
                adb = Adb(args.adb)
                report["device"] = adb.probe()
                if recipe:
                    for artifact in recipe["artifacts"].values():
                        actual = adb.shell("sha256sum " + shlex.quote(artifact["remote_path"])).split()
                        if not actual or actual[0] != artifact["sha256"]:
                            raise MeasurementError("On-device artifact differs from pinned local bytes")
                    report["recipe"] = recipe
                    report["actual_backend"] = "unverified"
                    report["backend_acceptance"] = "blocked; requires independent graph/placement evidence"
                    report["cache_policy"] = "fresh process each trial; OS page cache uncontrolled"
                    report["trials"] = []
                    for index in range(recipe["trials"]):
                        before = adb.context()
                        result = collect_trial(adb, recipe)
                        result.update(index=index + 1, before=before, after=adb.context())
                        report["trials"].append(result)
                        checkpoint(output, report)
                    report["status"] = "incomplete" if all(t["status"] == "observed" for t in report["trials"]) else "failed"
                else:
                    report["status"] = "observed_inventory_only"
            except MeasurementError as error:
                report["blocker"] = str(error)
            except KeyboardInterrupt:
                report["status"] = "interrupted"
                report["blocker"] = "User cancelled collection; no unobserved metrics inferred"
            except (OSError, subprocess.SubprocessError):
                report["status"] = "failed"
                report["blocker"] = "Collection I/O failed; raw diagnostics suppressed"
        finally:
            checkpoint(output, report)
        print(json.dumps({"status": report["status"], "evidence": str(output)}))
        return 0 if report["status"] == "observed_inventory_only" else 2
    except (MeasurementError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "failed", "error_type": type(error).__name__}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
