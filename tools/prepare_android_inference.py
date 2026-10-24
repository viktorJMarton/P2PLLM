"""Build the pinned JNI adapter and stage verified offline Android assets.

Requires the existing pinned ExecuTorch Android static install. Never exports,
downloads, loads or executes a model. Build output contains no inference data.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

try:
    from build_phone_runner import ROOT, VS, digest, git
    from run_checks import CheckError, execute, safe_path, utc_now, write_json
    from runtime_artifacts import verified_flatc
except ModuleNotFoundError:
    from tools.build_phone_runner import ROOT, VS, digest, git
    from tools.run_checks import CheckError, execute, safe_path, utc_now, write_json
    from tools.runtime_artifacts import verified_flatc

RUNTIME_REVISION = "3b60683923245cf472b7323426920e15623ba361"
MODEL = (468633472, "07786b553d9661d36431426d06c268f385d453314f6722ca79f66c7e79653b48")
TOKENIZER = (11422654, "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4")
LICENSE = (11343, "832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e")


def verify_file(path, expected):
    if not path.is_file() or path.stat().st_size != expected[0] or digest(path) != expected[1]:
        raise CheckError("Artifact missing or hash mismatch")


def verified_copy(source, destination, expected):
    source = safe_path(ROOT, source)
    destination = safe_path(ROOT, destination)
    partial = safe_path(ROOT, destination.with_suffix(destination.suffix + ".partial"))
    verify_file(source, expected)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, partial)
    verify_file(partial, expected)
    partial.replace(destination)


def stage_notices(source, install, ndk, assets):
    """Preserve pinned component notices; inventory is provenance, not legal certification."""
    tokenizer = source / "extension/llm/tokenizers"
    xnn = source / "backends/xnnpack/third-party"
    components = {
        "executorch": (source, False),
        "tokenizers": (tokenizer, False),
        "XNNPACK": (xnn / "XNNPACK", True),
        "pthreadpool": (xnn / "pthreadpool", True),
        "cpuinfo": (xnn / "cpuinfo", True),
        "FP16": (xnn / "FP16", True),
        "FXdiv": (xnn / "FXdiv", True),
        "flatbuffers": (source / "third-party/flatbuffers", True),
        "gflags": (source / "third-party/gflags", True),
        "executorch-json": (source / "third-party/json", True),
        "eigen": (source / "kernels/optimized/third-party/eigen", True),
        **{name: (tokenizer / "third-party" / name, True)
           for name in ("abseil-cpp", "json", "pcre2", "re2", "sentencepiece")},
        "KleidiAI": (install / "kleidiai-source", True),
        "android-ndk-libcxx": (ndk, False),
    }
    inventory = {"schema_version": 1, "scope": "Pinned linked runtime component notices; no legal certification",
                 "runtime_revision": RUNTIME_REVISION, "components": []}
    target = safe_path(ROOT, assets / "runtime-notices")
    for name, (component, recursive) in sorted(components.items()):
        component = safe_path(ROOT, component)
        if not component.is_dir():
            raise CheckError("Runtime notice component missing: " + name)
        candidates = component.rglob("*") if recursive else component.iterdir()
        paths = sorted(p for p in candidates if p.is_file() and (
            p.name.upper().startswith(("LICENSE", "LICENCE", "COPYING", "NOTICE", "COPYRIGHT")) or
            any(part.upper() in ("LICENSES", "LICENCES") for part in p.relative_to(component).parts[:-1])))
        if not paths:
            raise CheckError("Runtime component notices missing: " + name)
        record = {"name": name, "source_directory": component.relative_to(ROOT).as_posix(), "files": []}
        if component.is_relative_to(source):
            record["git_revision"] = git(component, "rev-parse", "HEAD")
        elif name == "KleidiAI":
            record["archive_sha256"] = "b147799b94c51f5e57492930bfd9e5294fb7ffe44fee1dbcd3f8048adeedd5e3"
        else:
            record["ndk_version"] = "27.0.12077973"
        for path in paths:
            path = safe_path(ROOT, path)
            relative = Path(name) / path.relative_to(component)
            expected = (path.stat().st_size, digest(path))
            verified_copy(path, target / relative, expected)
            record["files"].append({"path": relative.as_posix(), "bytes": expected[0], "sha256": expected[1]})
        inventory["components"].append(record)
    inventory_path = safe_path(ROOT, target / "inventory.json")
    partial = safe_path(ROOT, target / "inventory.json.partial")
    partial.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    partial.replace(inventory_path)
    return {"path": inventory_path.relative_to(ROOT).as_posix(), "sha256": digest(inventory_path),
            "components": len(inventory["components"])}


def run(output, jobs):
    output = safe_path(ROOT, output)
    if not output.is_relative_to(ROOT / ".artifacts") or output.exists():
        raise CheckError("Output must be a new .artifacts directory")
    output.mkdir(parents=True)
    report = {"schema_version": 1, "run_kind": "android_jni_build_and_asset_staging",
              "started_at": utc_now(), "status": "failed", "commands": [],
              "runtime_revision": RUNTIME_REVISION, "model_execution": False}
    previous_path = os.environ.get("PATH", "")
    try:
        source = safe_path(ROOT, ".artifacts/native/executorch")
        install = safe_path(ROOT, ".artifacts/native/android-1.5.1")
        build = safe_path(ROOT, ".artifacts/native/p2p-inference-1")
        safe_path(ROOT, install / "examples/models/p2p-llama")
        baseline = json.loads((ROOT / "config/model-baselines.json").read_text())
        if baseline["runtime"]["revision"] != RUNTIME_REVISION or git(source, "rev-parse", "HEAD") != RUNTIME_REVISION:
            raise CheckError("Native runtime revision mismatch")
        if git(source, "status", "--porcelain", "--untracked-files=normal"):
            raise CheckError("Native source or submodule modified")
        if any(line.startswith(("+", "U")) for line in git(source, "submodule", "status", "--recursive").splitlines()):
            raise CheckError("Native submodule revision mismatch")
        model = safe_path(ROOT, ".artifacts/exports/qwen-runtime-20261023-003/qwen3_0_6b.pte")
        model_dir = safe_path(ROOT, ".artifacts/models/Qwen3-0.6B-c1899de289a04d12100db370d81485cdf75e47ca")
        for path, expected in ((model, MODEL), (model_dir / "tokenizer.json", TOKENIZER), (model_dir / "LICENSE", LICENSE)):
            verify_file(path, expected)
        if not (install / "lib/cmake/ExecuTorch/executorch-config.cmake").is_file():
            raise CheckError("Pinned Android static runtime install missing")
        python = safe_path(ROOT, ".artifacts/venvs/qwen-export/Scripts/python.exe")
        flatc = safe_path(ROOT, verified_flatc(ROOT, baseline, python)["executable"])
        flatcc = safe_path(ROOT, source / "third-party/flatcc/bin/Release/flatcc.exe")
        if not flatcc.is_file():
            raise CheckError("Existing host flatcc missing")
        ndk = safe_path(ROOT, ".artifacts/toolchains/android-sdk/ndk/27.0.12077973")
        lock = json.loads((ROOT / "config/development-windows.json").read_text())
        if "ndk;27.0.12077973" not in lock["android"]:
            raise CheckError("NDK lock mismatch")
        cmake, ninja = VS / "CMake/bin/cmake.exe", VS / "Ninja/ninja.exe"
        os.environ["PATH"] = os.pathsep.join((str(ninja.parent), str(cmake.parent), previous_path))

        def phase(name, argv, timeout=300):
            result = execute({"id": name, "argv": [str(x) for x in argv], "timeout_seconds": timeout}, ROOT)
            report["commands"].append(result)
            write_json(output / (name + ".json"), result)
            if result["status"] != "passed":
                raise CheckError("Build phase failed: " + name)

        flags = ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}",
                 f"-DCMAKE_TOOLCHAIN_FILE={(ndk / 'build/cmake/android.toolchain.cmake').as_posix()}",
                 "-DANDROID_ABI=arm64-v8a", "-DANDROID_PLATFORM=android-26", "-DCMAKE_BUILD_TYPE=Release",
                 f"-DCMAKE_INSTALL_PREFIX={install.as_posix()}", f"-DEXECUTORCH_INSTALL={install.as_posix()}",
                 f"-DEXECUTORCH_SOURCE={source.as_posix()}", f"-DPYTHON_EXECUTABLE={python.as_posix()}",
                 f"-DFLATC_EXECUTABLE={flatc.as_posix()}", f"-DFLATCC_EXECUTABLE={flatcc.as_posix()}",
                 f"-Dexecutorch_DIR={(install / 'lib/cmake/ExecuTorch').as_posix()}",
                 f"-Dgflags_DIR={(install / 'third-party/gflags').as_posix()}",
                 "-DEXECUTORCH_BUILD_KERNELS_OPTIMIZED=ON", "-DSUPPORT_REGEX_LOOKAHEAD=ON"]
        phase("jni-configure", [cmake, "-S", ROOT / "native/executorch-adapter", "-B", build, *flags])
        phase("jni-build", [cmake, "--build", build, "--target", "p2p_inference", "--parallel", jobs], 1200)
        binary = safe_path(ROOT, build / "libp2p_inference.so")
        native_dir = safe_path(ROOT, "android/app/src/main/jniLibs/arm64-v8a")
        assets = safe_path(ROOT, "android/app/build/generated/localModelAssets/local-model")
        verified_copy(model, assets / "model.pte", MODEL)
        verified_copy(model_dir / "tokenizer.json", assets / "tokenizer.json", TOKENIZER)
        verified_copy(model_dir / "LICENSE", assets / "LICENSE", LICENSE)
        report["runtime_notices"] = stage_notices(source, install, ndk, assets)
        binary_expected = (binary.stat().st_size, digest(binary))
        verified_copy(binary, native_dir / binary.name, binary_expected)
        # ExecuTorch links the approved NDK shared C++ runtime.
        cxx = safe_path(ROOT, ndk / "toolchains/llvm/prebuilt/windows-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so")
        verified_copy(cxx, native_dir / cxx.name, (cxx.stat().st_size, digest(cxx)))
        report.update(status="passed", library={"path": (native_dir / binary.name).relative_to(ROOT).as_posix(),
                      "bytes": binary_expected[0], "sha256": binary_expected[1]},
                      assets_directory=assets.relative_to(ROOT).as_posix(),
                      model={"bytes": MODEL[0], "sha256": MODEL[1]},
                      tokenizer={"bytes": TOKENIZER[0], "sha256": TOKENIZER[1]})
    except (CheckError, OSError, ValueError, subprocess.SubprocessError) as error:
        report["reason"] = str(error) if type(error) is CheckError else "build_precondition_or_io_failed"
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
