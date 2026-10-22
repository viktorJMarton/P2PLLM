"""Pinned Windows development cache, activation, doctor and Android build entry.

Set P2PLLM_TOOLCHAIN_ROOT to share a versioned cache across isolated worktrees.
No global PATH is rewritten. SDK acceptance is explicit and scoped to this lock.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "config/development-windows.json"


def digest(path, algorithm="sha256"):
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def matches_version(output, expected):
    # Match an entire version token; reject near versions and prerelease suffixes.
    return re.search(r"(?<![A-Za-z0-9_.])" + re.escape(expected) +
                     r"(?![A-Za-z0-9_.-])", output) is not None


def download(package, cache):
    archive = cache / "downloads" / package["url"].rsplit("/", 1)[1]
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        temporary = archive.with_suffix(".part")
        with urllib.request.urlopen(package["url"], timeout=120) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        temporary.rename(archive)
    if digest(archive) != package["sha256"]:
        raise ValueError(f"Checksum mismatch: {archive.name}; inspect cache before retrying")
    if "size" in package and archive.stat().st_size != package["size"]:
        raise ValueError(f"Archive size mismatch: {archive.name}")
    return archive


def install_zip(archive, target, staging):
    if target.exists():
        return
    stage = staging / f"{target.parent.name}-{target.name}-{os.getpid()}"
    stage.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as source:
        for entry in source.infolist():
            if not (stage / entry.filename).resolve().is_relative_to(stage.resolve()):
                raise ValueError("Unsafe archive path")
        source.extractall(stage)
    children = list(stage.iterdir())
    if len(children) != 1 or not children[0].is_dir():
        raise ValueError("Expected one archive root directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    children[0].rename(target)
    stage.rmdir()


def configuration():
    if os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        raise ValueError("This verified bootstrap profile targets Windows x86_64; other hosts use their documented platform setup")
    return json.loads(LOCK.read_text(encoding="utf-8"))


def environment(cache, config):
    jdk_root = cache / f"jdk-{config['jdk']['version']}"
    # Clean installer removes the archive wrapper; support the earlier manually
    # extracted wrapper too, without permitting two ambiguous Java homes.
    direct = jdk_root / "bin/java.exe"
    java = ([direct] if direct.is_file() else []) + list(jdk_root.glob("*/bin/java.exe"))
    if len(java) != 1:
        raise ValueError("Pinned JDK is missing; run install first")
    jdk = java[0].parent.parent
    sdk = cache / "android-sdk"
    env = os.environ.copy()
    env.update(JAVA_HOME=str(jdk), ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk),
               ANDROID_NDK_HOME=str(sdk / "ndk/27.0.12077973"),
               GRADLE_USER_HOME=str(cache / "gradle-cache"))
    env["PATH"] = os.pathsep.join([str(jdk / "bin"), str(cache / "rust-tools/bin"),
                                  str(sdk / "cmdline-tools/16.0/bin"), env.get("PATH", "")])
    return env


def install(cache, config, accepted):
    cache.mkdir(parents=True, exist_ok=True)
    lock = cache / "bootstrap.lock"
    # Single bootstrap writer per shared cache. A crash leaves an inspectable
    # lock; never silently delete another installer's lock or partial staging.
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(descriptor, str(os.getpid()).encode())
        jdk_archive = download(config["jdk"], cache)
        install_zip(jdk_archive, cache / f"jdk-{config['jdk']['version']}", cache / "staging")
        scope = hashlib.sha256(json.dumps({"packages": config["android"],
            "license_id": config["android_license"]["id"],
            "license_sha256": config["android_license"]["sha256"]},
            sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        acceptance = cache / "sdk-license-acceptance.json"
        previous = json.loads(acceptance.read_text(encoding="utf-8")) if acceptance.exists() else {}
        if not accepted and previous.get("lock_sha256") != scope:
            raise ValueError("SDK license owner acceptance required for this package lock; inspect license then use --accept-sdk-license")
        license_path = cache / "ANDROID-SDK-LICENSE.txt"
        if not license_path.exists():
            with urllib.request.urlopen(config["android_license"]["metadata_url"], timeout=60) as response:
                repository = ET.fromstring(response.read())
            license_text = next(item.text for item in repository.findall("license")
                                if item.attrib.get("id") == config["android_license"]["id"])
            # The Windows lock records the historical CRLF source snapshot.
            license_path.write_text(license_text, encoding="utf-8", newline=None)
        if digest(license_path) != config["android_license"]["sha256"]:
            raise ValueError("SDK license text changed; review/update the locked scope before acceptance")
        acceptance.write_text(json.dumps({"lock_sha256": scope,
            "accepted_at": previous.get("accepted_at", datetime.now(timezone.utc).isoformat()),
            "package_ids": list(config["android"])}, indent=2) + "\n", encoding="utf-8")
        sdk = cache / "android-sdk"
        for key, package in config["android"].items():
            archive = download(package, cache)
            target = sdk.joinpath(*key.split(";"))
            install_zip(archive, target, cache / "staging")
            print(f"Verified package: {key}", flush=True)
        (sdk / "licenses").mkdir(exist_ok=True)
        text = license_path.read_text(encoding="utf-8").strip()
        (sdk / "licenses/android-sdk-license").write_text(hashlib.sha1(text.encode()).hexdigest() + "\n", encoding="utf-8", newline="\n")
        receipt = {"lock_sha256": scope, "jdk_sha256": digest(jdk_archive),
                   "packages": {key: value["sha256"] for key, value in config["android"].items()}}
        (cache / "installed.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    finally:
        os.close(descriptor)
        lock.unlink()


def doctor(cache, config):
    env = environment(cache, config)
    probes = []
    for label, command in (
        ("java", [str(Path(env["JAVA_HOME"]) / "bin/java.exe"), "-version"]),
        ("javac", [str(Path(env["JAVA_HOME"]) / "bin/javac.exe"), "-version"]),
        ("rust", ["rustup", "run", "1.88.0", "rustc", "--version"]),
        ("cargo-ndk", ["cargo", "ndk", "--version"]),
    ):
        try:
            result = subprocess.run(command, env=env, cwd=REPO, capture_output=True, text=True, timeout=30)
            probes.append({"tool": label, "exit_code": result.returncode,
                           "version": (result.stdout + result.stderr).strip().splitlines()[:3]})
        except (OSError, subprocess.TimeoutExpired):
            probes.append({"tool": label, "exit_code": None, "version": []})
    files = ["platforms/android-35/android.jar", "build-tools/35.0.0/aapt2.exe",
             "cmdline-tools/16.0/bin/sdkmanager.bat",
             "ndk/27.0.12077973/toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe"]
    missing = [name for name in files if not (Path(env["ANDROID_HOME"]) / name).is_file()]
    expected = {"java": config["jdk"]["version"], "javac": config["jdk"]["version"],
                "rust": config["tools"]["rust"], "cargo-ndk": config["tools"]["cargo_ndk"]}
    for probe in probes:
        probe["expected_version"] = expected[probe["tool"]]
        probe["version_matches"] = matches_version(" ".join(probe["version"]), expected[probe["tool"]])
    complete = not missing and all(p["exit_code"] == 0 and p["version_matches"] for p in probes)
    print(json.dumps({"status": "passed" if complete else "unavailable", "tools": probes,
                      "missing_sdk_files": missing, "cache": str(cache)}, indent=2))
    return 0 if complete else 2


def provision_rust(cache, config):
    """Explicit install action only; check/doctor/run never install tools."""
    env = environment(cache, config)
    version = config["tools"]["rust"]
    installed = subprocess.run(["rustup", "run", version, "rustc", "--version"],
                               capture_output=True, env=env, cwd=REPO, check=False)
    if installed.returncode:
        subprocess.run(["rustup", "toolchain", "install", version, "--profile", "minimal",
                        "--component", "rustfmt", "--component", "clippy"], env=env, cwd=REPO, check=True)
    subprocess.run(["rustup", "target", "add", config["tools"]["android_target"],
                    "--toolchain", version], env=env, cwd=REPO, check=True)
    ndk = subprocess.run(["cargo", "ndk", "--version"], capture_output=True, env=env, cwd=REPO, check=False)
    if ndk.returncode or not matches_version(ndk.stdout.decode("utf-8", errors="replace"), config["tools"]["cargo_ndk"]):
        subprocess.run(["cargo", "install", "cargo-ndk", "--version", config["tools"]["cargo_ndk"],
                        "--locked", "--root", str(cache / "rust-tools")], env=env, cwd=REPO, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "doctor", "run", "check", "android-build"])
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--accept-sdk-license", action="store_true")
    args, command_args = parser.parse_known_args()
    if args.action not in ("run", "check") and command_args:
        parser.error("unexpected command arguments")
    cache = (args.cache_root or Path(os.environ.get("P2PLLM_TOOLCHAIN_ROOT", REPO / ".artifacts/toolchains"))).resolve()
    try:
        config = configuration()
        if args.action == "install":
            install(cache, config, args.accept_sdk_license)
            provision_rust(cache, config)
            return 0
        if args.action == "doctor":
            return doctor(cache, config)
        env = environment(cache, config)
        if args.action == "android-build":
            subprocess.run(["cargo", "ndk", "-t", "arm64-v8a", "-o", "android/app/src/main/jniLibs",
                            "build", "--release", "--locked", "-p", "p2p-android-bridge"], cwd=REPO, env=env, check=True)
            command = [str(REPO / "android/gradlew.bat"), "-p", str(REPO / "android"), "--no-daemon", ":app:assembleDebug"]
        elif args.action == "check":
            command = [sys.executable, str(REPO / "tools/run_checks.py"), *command_args]
        else:
            command = command_args[1:] if command_args[:1] == ["--"] else command_args
            if not command:
                raise ValueError("run requires a command after --")
        return subprocess.run(command, cwd=REPO, env=env, check=False).returncode
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f"Development environment: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
