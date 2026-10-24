"""Build the pinned CPU/XNNPACK Android runner; never load a model.

Sources/submodules must already be provisioned under .artifacts/native/executorch.
Uses existing Visual Studio CMake/Ninja and the approved Android NDK.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
try:
    from run_checks import CheckError, execute, safe_path, utc_now, write_json
    from runtime_artifacts import RuntimeArtifactError, verified_flatc
except ModuleNotFoundError:
    from tools.run_checks import CheckError, execute, safe_path, utc_now, write_json
    from tools.runtime_artifacts import RuntimeArtifactError, verified_flatc

ROOT = Path(__file__).resolve().parents[1]
VS = Path("C:/Program Files/Microsoft Visual Studio/2022/Community/Common7/IDE/CommonExtensions/Microsoft/CMake")


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def git(source, *args):
    result = subprocess.run(["git", "-c", f"safe.directory={source.as_posix()}",
                             "-C", str(source), *args], capture_output=True,
                            text=True, timeout=30, check=True)
    return result.stdout.strip()


def run(output, jobs):
    source = safe_path(ROOT, ".artifacts/native/executorch")
    build = safe_path(ROOT, ".artifacts/native/android-1.5.1")
    host = safe_path(ROOT, ".artifacts/native/flatcc-host-1")
    python = safe_path(ROOT, ".artifacts/venvs/qwen-export/Scripts/python.exe")
    host_source = safe_path(ROOT, source / "third-party/flatcc")
    flatcc = safe_path(ROOT, host_source / "bin/Release/flatcc.exe")
    safe_path(ROOT, host_source / "lib")
    cmake, ninja = VS / "CMake/bin/cmake.exe", VS / "Ninja/ninja.exe"
    output = safe_path(ROOT, output)
    if not output.is_relative_to(ROOT / ".artifacts") or output.exists():
        raise CheckError("Output must be a new .artifacts directory")
    output.mkdir(parents=True)
    report = {"schema_version": 1, "run_kind": "android_runner_build_not_inference",
              "started_at": utc_now(), "status": "failed", "commands": [],
              "phone_measurement": False, "actual_backend": "not_observed"}
    previous_path = os.environ.get("PATH", "")
    try:
        # XNNPACK dependency sub-builds launch CMake/Ninja without forwarding
        # CMAKE_MAKE_PROGRAM. Scope their discovery to this process only.
        os.environ["PATH"] = os.pathsep.join((str(ninja.parent), str(cmake.parent), previous_path))
        baseline = json.loads((ROOT / "config/model-baselines.json").read_text())
        revision = baseline["runtime"]["revision"]
        if git(source, "rev-parse", "HEAD") != revision:
            raise CheckError("Native source revision mismatch")
        if git(source, "status", "--porcelain", "--untracked-files=normal"):
            raise CheckError("Native source or submodule modified")
        submodules = git(source, "submodule", "status", "--recursive").splitlines()
        # Optional backends remain uninitialized; every initialized gitlink must
        # match its parent and must have no tracked modifications.
        if any(line.startswith(("+", "U")) for line in submodules):
            raise CheckError("Native submodule revision mismatch")
        report.update(runtime_revision=revision, gitlinks=submodules, jobs=jobs)
        for name, tool in (("cmake", cmake), ("ninja", ninja)):
            version = subprocess.run([str(tool), "--version"], capture_output=True,
                                     text=True, check=True, timeout=10).stdout.splitlines()[0]
            report[name] = {"version": version, "sha256": digest(tool)}
        lock = json.loads((ROOT / "config/development-windows.json").read_text())
        ndk_key = next(key for key in lock["android"] if key.startswith("ndk;"))
        ndk = safe_path(ROOT, Path(".artifacts/toolchains/android-sdk/ndk") / ndk_key.split(";")[1])
        report["ndk"] = ndk_key
        compiler = verified_flatc(ROOT, baseline, python)
        flatc = safe_path(ROOT, compiler["executable"])
        report["flatc"] = compiler

        def phase(name, argv, timeout=1800):
            result = execute({"id": name, "argv": [str(x) for x in argv],
                              "timeout_seconds": timeout}, ROOT)
            report["commands"].append(result)
            write_json(output / (name + ".json"), result)
            if result["status"] != "passed":
                raise CheckError("Build phase failed: " + name)

        phase("host-flatcc-configure", [cmake, "-S", host_source, "-B", host,
              "-G", "Visual Studio 17 2022", "-A", "x64", "-DFLATCC_TEST=OFF",
              "-DFLATCC_REFLECTION=OFF", "-DFLATCC_ALLOW_WERROR=OFF"], 120)
        phase("host-flatcc-build", [cmake, "--build", host, "--config", "Release",
              "--target", "flatcc_cli", "--parallel", jobs], 300)
        report["flatcc_sha256"] = digest(flatcc)
        flags = ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}",
                 f"-DCMAKE_TOOLCHAIN_FILE={(ndk / 'build/cmake/android.toolchain.cmake').as_posix()}",
                 "-DANDROID_ABI=arm64-v8a", "-DANDROID_PLATFORM=android-26",
                 "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={build.as_posix()}",
                 f"-DPYTHON_EXECUTABLE={python.as_posix()}", "-DBUILD_TESTING=OFF",
                 "-DEXECUTORCH_ENABLE_LOGGING=ON", "-DEXECUTORCH_LOG_LEVEL=Error",
                 f"-DFLATC_EXECUTABLE={flatc.as_posix()}", f"-DFLATCC_EXECUTABLE={flatcc.as_posix()}"]
        flags += [f"-DEXECUTORCH_BUILD_{feature}=ON" for feature in (
            "EXTENSION_DATA_LOADER", "EXTENSION_FLAT_TENSOR", "EXTENSION_MODULE",
            "EXTENSION_TENSOR", "EXTENSION_NAMED_DATA_MAP", "EXTENSION_LLM",
            "EXTENSION_LLM_RUNNER", "XNNPACK", "KERNELS_OPTIMIZED", "KERNELS_QUANTIZED", "KERNELS_LLM")]
        # A failed upstream downloader still caches this directory. Unset only
        # that stale cache key so the hash-pinned download can resume.
        if not safe_path(ROOT, build / "kleidiai-source/CMakeLists.txt").is_file():
            flags += ["-UKLEIDIAI_SOURCE_DIR"]
        phase("android-runtime-configure", [cmake, "-S", source, "-B", build, *flags], 300)
        phase("android-runtime-build", [cmake, "--build", build, "--target", "install", "--parallel", jobs])
        runner_build = safe_path(ROOT, build / "examples/models/llama")
        phase("android-runner-configure", [cmake, "-S", source / "examples/models/llama", "-B",
              runner_build, *flags, "-DSUPPORT_REGEX_LOOKAHEAD=ON"], 300)
        phase("android-runner-build", [cmake, "--build", runner_build, "--target", "llama_main",
              "--parallel", jobs])
        binary = runner_build / "llama_main"
        report.update(status="passed", artifact={"path": binary.relative_to(ROOT).as_posix(),
                      "sha256": digest(binary), "bytes": binary.stat().st_size})
    except KeyboardInterrupt:
        report.update(status="interrupted", reason="cancelled")
        raise
    except (CheckError, OSError, ValueError, StopIteration, subprocess.SubprocessError) as error:
        report["reason"] = str(error) if type(error) in (CheckError, RuntimeArtifactError) else "build_precondition_or_io_failed"
    finally:
        os.environ["PATH"] = previous_path
        report["finished_at"] = utc_now()
        write_json(output / "report.json", report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.output, args.jobs))
    except CheckError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
