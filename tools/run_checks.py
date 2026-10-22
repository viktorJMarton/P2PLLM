"""Run declared local checks and collect bounded, sanitized provenance evidence."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import zipfile

try:
    from source_inventory import HASH_MODE, inventory_bytes, source_paths
except ModuleNotFoundError:
    from tools.source_inventory import HASH_MODE, inventory_bytes, source_paths


class CheckError(ValueError):
    """Invalid configuration or unsafe evidence destination."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def safe_path(root, value):
    """Confine paths, rejecting traversal and links even when they resolve inside."""
    path = Path(value)
    if ".." in path.parts:
        raise CheckError("Parent traversal is forbidden")
    path = path if path.is_absolute() else root / path
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise CheckError("Path must be inside the repository") from error
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise CheckError("Symlink and junction paths are forbidden")
    if not path.resolve().is_relative_to(root):
        raise CheckError("Path escapes repository")
    return path


def git_provenance(root):
    def read(*args):
        try:
            result = subprocess.run(
                ["git", "-c", f"safe.directory={root.as_posix()}", *args], cwd=root, capture_output=True, text=True,
                timeout=15, check=False,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    head = read("rev-parse", "HEAD")
    dirty = read("status", "--porcelain", "--untracked-files=normal")
    return {"head": head, "dirty": None if dirty is None else bool(dirty)}


def load_profile(path, name):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise CheckError("Unsupported profile schema version")
    profile = data.get("profiles", {}).get(name)
    if not isinstance(profile, dict):
        raise CheckError("Unknown check profile")
    commands = profile.get("commands")
    artifacts = profile.get("artifacts")
    if not isinstance(commands, list) or not isinstance(artifacts, list):
        raise CheckError("Profile commands and artifacts must be lists")
    ids = set()
    for command in commands:
        if not isinstance(command, dict):
            raise CheckError("Invalid command")
        identifier = command.get("id")
        argv = command.get("argv")
        timeout = command.get("timeout_seconds")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise CheckError("Command IDs must be nonempty and unique")
        ids.add(identifier)
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
            raise CheckError("Command argv must contain nonempty strings")
        if type(timeout) is not int or timeout <= 0:
            raise CheckError("Command timeout must be a positive integer")
    if any(not isinstance(a, str) or not a or Path(a).is_absolute() for a in artifacts):
        raise CheckError("Artifact paths must be relative nonempty strings")
    if "unavailable_reason" in profile and not isinstance(profile["unavailable_reason"], str):
        raise CheckError("Unavailable reason must be a string")
    return profile


def expand(value, root):
    replacements = {
        "{python}": sys.executable,
        "{gradlew}": str(root / "android" / ("gradlew.bat" if os.name == "nt" else "gradlew")),
        "{exe_suffix}": ".exe" if os.name == "nt" else "",
    }
    for token, replacement in replacements.items():
        value = value.replace(token, replacement)
    return value


class WindowsJob:
    """Own child process lifetimes without taskkill or administrative rights."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in
                        ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                         "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", IoCounters),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.api.CreateJobObjectW.restype = wintypes.HANDLE
        self.api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, process):
        import ctypes
        if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def execute(command, root):
    argv = [expand(a, root) for a in command["argv"]]
    result = {
        "id": command["id"], "argv": argv,
        "timeout_seconds": command["timeout_seconds"], "started_at": utc_now(),
        "exit_code": None,
    }
    job = None
    process = None
    try:
        job = WindowsJob() if os.name == "nt" else None
        process = subprocess.Popen(argv, cwd=root, shell=False, start_new_session=os.name != "nt")
        if job:
            try:
                job.assign(process)
            except OSError:
                process.kill()
                process.wait(timeout=5)
                raise
        try:
            code = process.wait(timeout=command["timeout_seconds"])
            result.update(exit_code=code, status="passed" if code == 0 else "failed")
        except subprocess.TimeoutExpired:
            cleanup = True
            try:
                if os.name == "nt":
                    job.close()
                else:
                    os.killpg(process.pid, signal.SIGKILL)
            except (OSError, subprocess.TimeoutExpired):
                cleanup = False
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            result.update(status="failed", reason="timeout" if cleanup else "timeout_cleanup_failed")
    except FileNotFoundError:
        result.update(status="unavailable", reason="executable_not_found")
    except subprocess.TimeoutExpired:
        result.update(status="failed", reason="timeout")
    except OSError:
        result.update(status="failed", reason="process_launch_error")
    finally:
        if job:
            job.close()
        elif process is not None and os.name != "nt":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    result["finished_at"] = utc_now()
    return result


def source_snapshot(root, destination):
    digest = hashlib.sha256()
    count = 0
    try:
        for path in source_paths(root):
            if path == destination or destination in path.parents:
                continue
            safe_path(root, path)
            name = path.relative_to(root).as_posix().encode("utf-8")
            content = inventory_bytes(path)
            digest.update(len(name).to_bytes(8, "big"))
            digest.update(name)
            digest.update(hashlib.sha256(content).digest())
            count += 1
        return {"hash_mode": HASH_MODE, "sha256": digest.hexdigest(), "file_count": count}
    except (OSError, CheckError, subprocess.SubprocessError, UnicodeError):
        return None


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def make_bundle(destination, report_path, artifact_paths, root):
    """Stream only allowlisted regular files and hash exactly the bytes archived."""
    manifest = {"schema_version": 1, "files": []}
    bundle_path = destination / "bundle.zip"
    created = False
    try:
        with bundle_path.open("xb") as bundle_file, zipfile.ZipFile(bundle_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            created = True
            entries = [("report.json", report_path)] + [
                ("artifacts/" + path.relative_to(root).as_posix(), path) for path in artifact_paths
            ]
            for name, path in entries:
                safe_path(root, path)
                digest = hashlib.sha256()
                size = 0
                with path.open("rb") as source, archive.open(name, "w", force_zip64=True) as target:
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                        size += len(chunk)
                        target.write(chunk)
                manifest["files"].append({"path": name, "sha256": digest.hexdigest(), "size_bytes": size})
            archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    except Exception:
        # Never leave a partial ZIP that could be mistaken for a valid package.
        if created:
            bundle_path.unlink(missing_ok=True)
        raise


def run_profile(repo_root, profile_name, work_id, run_id, output_dir=None, bundle=False, config_path=None):
    root = Path(repo_root).resolve()
    for name, value in (("profile", profile_name), ("work_id", work_id), ("run_id", run_id)):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
            raise CheckError(f"Unsafe {name}")
    if not re.fullmatch(r"WORK-\d{4}", work_id):
        raise CheckError("Work ID must have WORK-NNNN format")
    profile = load_profile(Path(config_path) if config_path else root / "config/check-profiles.json", profile_name)
    destination = safe_path(root, output_dir or f".artifacts/checks/{work_id}/{run_id}/{profile_name}")
    # Validate all paths before launching commands or reserving evidence output.
    artifacts = [safe_path(root, expand(a, root)) for a in profile["artifacts"]]
    if len(set(artifacts)) != len(artifacts):
        raise CheckError("Duplicate artifact paths")
    if any(path == destination or destination in path.parents or path in destination.parents for path in artifacts):
        raise CheckError("Artifacts and report destination overlap")
    provenance = git_provenance(root)
    snapshot = source_snapshot(root, destination)
    try:
        destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise CheckError("Output destination already exists; choose a new run ID") from error
    report = {
        "schema_version": 1, "work_id": work_id, "run_id": run_id,
        "profile": profile_name, "started_at": utc_now(),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "git": provenance, "source_before": snapshot, "commands": [], "artifacts": [],
        "status": "unavailable", "bundle_requested": bundle,
    }
    reason = profile.get("unavailable_reason")
    if reason:
        report["reason"] = reason
    elif not profile["commands"]:
        report["reason"] = "Profile has no checks"
    else:
        stopped = False
        for command in profile["commands"]:
            if stopped:
                report["commands"].append({"id": command["id"], "argv": [expand(a, root) for a in command["argv"]],
                                           "status": "not_run", "exit_code": None, "reason": "previous_check_did_not_pass"})
                continue
            result = execute(command, root)
            report["commands"].append(result)
            stopped = result["status"] != "passed"
        statuses = {c["status"] for c in report["commands"]}
        report["status"] = "failed" if "failed" in statuses else "unavailable" if "unavailable" in statuses else "passed"
        if provenance["head"] is None or provenance["dirty"] is None or snapshot is None:
            if report["status"] != "failed":
                report["status"] = "unavailable"
            report["reason"] = "Git provenance unavailable"
        for path in artifacts:
            try:
                safe_path(root, path)
                valid = path.is_file()
            except (CheckError, OSError):
                valid = False
            report["artifacts"].append({"path": path.relative_to(root).as_posix(), "status": "present" if valid else "missing_or_unsafe"})
            if not valid:
                report["status"] = "failed"
    report["source_after"] = source_snapshot(root, destination)
    report["git_after"] = git_provenance(root)
    if snapshot is not None and (report["source_after"] != snapshot or report["git_after"]["head"] != provenance["head"]):
        report.update(status="failed", reason="Source changed during checks")
    report["finished_at"] = utc_now()
    report_path = destination / "report.json"
    write_json(report_path, report)
    if bundle and report["status"] == "passed":
        try:
            make_bundle(destination, report_path, artifacts, root)
        except (OSError, CheckError, zipfile.BadZipFile):
            report.update(status="failed", reason="Bundle creation failed")
            # This run owns the exclusive destination; update its own report.
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return {"passed": 0, "failed": 1, "unavailable": 2}[report["status"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--bundle", action="store_true")
    args = parser.parse_args()
    try:
        return run_profile(Path(__file__).resolve().parents[1], args.profile, args.work_id,
                           args.run_id, args.output_dir, args.bundle)
    except (CheckError, OSError, json.JSONDecodeError) as error:
        print(f"Check runner: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
