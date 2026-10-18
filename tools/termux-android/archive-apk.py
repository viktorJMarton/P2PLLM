#!/usr/bin/env python3
"""Archive a successful Android debug APK under its SemVer minor release directory."""
from __future__ import annotations
import argparse
import hashlib
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADLE = ROOT / "android/app/build.gradle.kts"
DEFAULT_APK = ROOT / "android/app/build/outputs/apk/debug/app-debug.apk"

def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", type=Path, default=DEFAULT_APK)
    parser.add_argument("--work-id", default="WORK-0008")
    parser.add_argument("--allow-existing", action="store_true", help="Allow exact identical archive only")
    args = parser.parse_args()
    source = args.apk.resolve()
    if not source.is_file() or source.stat().st_size == 0:
        fail(f"APK missing or empty: {source}")
    gradle = GRADLE.read_text()
    version_match = re.search(r'versionName\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', gradle)
    code_match = re.search(r'versionCode\s*=\s*(\d+)', gradle)
    if not version_match or not code_match:
        fail("versionName/versionCode missing or non-literal in app/build.gradle.kts")
    version = version_match.group(1)
    major, minor, patch = map(int, version.split("."))
    if patch != 0:
        fail("This archival flow is restricted to minor versions X.Y.0")
    branch = subprocess.check_output(["git", "-C", str(ROOT), "branch", "--show-current"], text=True).strip()
    expected_branch = "build/termux-android-arm64"
    is_ci = __import__("os").environ.get("GITHUB_ACTIONS") == "true"
    ci_branch = __import__("os").environ.get("GITHUB_REF_NAME", "")
    if branch != expected_branch and not (is_ci and ci_branch == expected_branch):
        fail(f"Refusing archive outside {expected_branch}: local={branch!r}, CI={ci_branch!r}")
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    target_dir = ROOT / "releases/android" / f"v{version}" / "debug"
    destination = target_dir / f"P2PLLM-v{version}-debug.apk"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if destination.exists():
        existing_digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        if not args.allow_existing or digest != existing_digest:
            fail(f"Existing APK archived at {destination}; refusing overwrite")
        print(f"Existing identical artifact: {destination}")
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (target_dir / "SHA256SUMS").write_text(f"{digest}  {destination.name}\n")
    (target_dir / "DEBUG-NOTES.md").write_text(
        f"# P2PLLM v{version} — Debug notes\n\n"
        f"- Version name: `{version}`\n- Version code: `{code_match.group(1)}`\n"
        f"- Build type: debug, not production-signed\n- WORK item: `{args.work_id}`\n"
        f"- Source commit at build time: `{commit}`\n- Branch: `{branch}`\n"
        f"- Archived UTC: {timestamp}\n- ABI: arm64-v8a\n"
        f"- Build command: `bash tools/termux-android/build.sh`\n"
        f"- APK output: `{destination.relative_to(ROOT)}`\n"
        f"- SHA-256: `{digest}`\n\n"
        "## Verification\n\n"
        "- [x] Build command exited successfully and a nonempty APK was found\n"
        "- [ ] Installed and launched on device for this build (requires separate evidence)\n"
        "- [ ] Kotlin–Rust smoke test documented for this build\n\n"
        "## Known limitations\n\n"
        "Initial Android bootstrap/status screen only. Private computation, learning, "
        "peer networking and LLM inference are not validated by APK creation.\n"
    )
    print(f"Archived: {destination}")
    print(f"Notes: {target_dir / 'DEBUG-NOTES.md'}")
    print("APK is ignored by Git; publishing requires explicit review and authorization.")

if __name__ == "__main__":
    main()
