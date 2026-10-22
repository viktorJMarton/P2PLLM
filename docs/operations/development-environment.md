# Reproducible development environment

WORK-0012 provisions the current Windows x86_64 host. The checked-in lock is
[config/development-windows.json](../../config/development-windows.json):
Microsoft JDK17.0.20.1, Android SDK35 revision2, Build Tools35.0.0,
Command-line Tools16.0, NDK27.0.12077973, Rust1.88.0 and cargo-ndk3.5.4.
Gradle8.11.1 and its SHA256 remain pinned by the wrapper. The reference Linux
target and existing Linux CI use their own documented provisioning; this verified
Windows bootstrap is not a claim that other host profiles were tested.

## Install and use

Prerequisites: Python3.11+, Git, rustup and the Windows C/C++ build toolchain
needed by bundled SQLite. Use an actual installed Python executable if the
WindowsApps alias fails. Installation downloads only locked archives, verifies
SHA256/size, uses staged extraction and never rewrites the global PATH.

```text
python tools/dev_env.py install --accept-sdk-license
python tools/dev_env.py doctor
python tools/dev_env.py check --profile rust --work-id WORK-0010 --run-id local-001 --bundle
python tools/dev_env.py check --profile android --work-id WORK-0011 --run-id local-001 --bundle
python tools/dev_env.py android-build
python tools/dev_env.py run -- <command and arguments>
```

The owner approved the four exact SDK packages/license in this session. Future
operators accept their own reviewed scope; approval is not inferred from a file
claim. A cache receipt preserves that accepted Android-package/license scope,
so unrelated tool or formatting changes do not require accepting identical terms
again. No new SDK terms or extra packages are accepted automatically.

`install` also ensures the pinned Rust toolchain/Android target and cargo-ndk.
When a suitable cargo-ndk is absent, its pinned binary is installed in the
cache-local rust-tools directory. `doctor`, `check`, `run` and `android-build`
do not install missing tools. Doctor compares exact version tokens and expected
SDK files; it is not a cryptographic audit of a locally modified extracted cache.
Keep that cache trusted and re-provision if its contents are suspect.

## Parallel departments and CI

Default cache: `.artifacts/toolchains/`, ignored by Git. Set
`P2PLLM_TOOLCHAIN_ROOT` to one absolute persistent cache path shared by isolated
worktrees on the same host, or use `--cache-root PATH`. Do not share compiled
project output directories across different worktrees. SDK/JDK versions have
separate directories; dependency updates require a lock/provenance change.
Bootstrap has one writer lock; inspect a stale lock after an interrupted install
instead of deleting another active installer's files. Downloads and Gradle
artifacts are reusable; Gradle handles its cache locks. CI caching is a platform
job configuration, not an installed remote guarantee from this document.

The environment wrapper activates JAVA_HOME, ANDROID_HOME/ANDROID_SDK_ROOT,
ANDROID_NDK_HOME, GRADLE_USER_HOME and child PATH for that command only. Python
and Rust reports retain actual platform/source identity. Each department keeps
its own WORK/run ID and report directory. Freeze source/journal writers before
final profile runs; ordinary meetings use read-prefix receipts without global
waiting. See [department workflow](department-workflow.md).

The debug APK is `android/app/build/outputs/apk/debug/app-debug.apk`. A successful
build is not a device test or a production release. Local debug signing is not
release signing. Optional Platform-Tools/emulator/device provisioning remains
separate; the approved package scope here does not silently include extra terms.
