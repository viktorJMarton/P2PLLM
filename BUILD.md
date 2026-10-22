# Build and verification status

## Available now
Department check profiles and evidence packaging are described in
[the common workflow](docs/operations/department-workflow.md). Python 3.11+
provides the portable entry point:

```text
python tools/run_checks.py --profile workflow --work-id WORK-0009 --run-id local-001 --bundle
```

Use a fresh run ID/output directory on every invocation. `docs`, `workflow`,
`rust` and `android` select existing checks/build commands; their actual outcome
depends on the installed toolchains. `storage`, `interop`, `device` and `privacy`
explicitly return unavailable until their acceptance harnesses exist. A passing
JVM task with no tests is not evidence of UI coverage. No profile certifies a
private model or enables release automation.

Source inventory uses `hash_mode: utf8-lf-v1`: UTF-8 text without NULs is hashed
with LF line endings, binary files retain exact bytes, paths use `/`. This makes
source identity portable across Windows/Linux checkouts. Built artifacts and
bundle SHA-256 checksums always use exact bytes. After intentional source edits,
run `python tools/update_manifest.py` before the `docs` profile; validation never
updates its own expected inventory. Both scripts read/write UTF-8 explicitly.

With Python >=3.11, `python3 tools/validate_package.py` checks the documentation package, identifiers, manifests, example config/schema (the validator implements only the schema keywords used here), event schema, relative links and BPMN structure. It does not compile product code or render PlantUML.

## WORK-0001 implementation in progress
`just check`, `just test`, `just build-desktop` and
`just build-android` are defined. The latter requires an external Android
SDK/NDK and toolchain. `just test-interop` and `just benchmark` explicitly
exit unavailable until their work items exist; neither is a passing check.

Targets: Linux x86_64 desktop reference, Android arm64-v8a device; Android emulator can check UI/bridge, not certify actual NPU/energy behavior. Build prerequisites and exact JDK/NDK/SDK/Rust/Python versions are to be measured and pinned by WORK-0001. Inspect available toolchains rather than assuming the current execution host has Android support.

Bootstrap acceptance: reproducible workspace build, minimal CLI status, Kotlin→Rust status call, isolated check/test jobs, dependency locks. The local Rust workspace, CLI status and host UniFFI binding generator have built and been tested on Ubuntu 25.04 aarch64 proot with Rust 1.88.0. Gradle 8.11.1 launched with JDK 17, Android tasks configured and debug runtime dependencies resolved. Android APK and device bridge call have not been built or run in this environment. Unsupported network AI operations fail closed.

Future CI: rustfmt, Clippy, tests with --locked; Gradle lint/JVM/device tests; protobuf compatibility; DB crash-recovery; malformed message handling; backend policy denial; conformance and independent test peer. Run only checks relevant to the patch. Physical-device thermal/energy tests are separately labeled.
