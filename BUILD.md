# Build and verification status

## Available now
With Python >=3.11, `python3 tools/validate_package.py` checks the documentation package, identifiers, manifests, example config/schema (the validator implements only the schema keywords used here), event schema, relative links and BPMN structure. It does not compile product code or render PlantUML.

## Bootstrap must implement
`just check`, `just test`, `just build-desktop`, `just build-android`, `just test-interop`, `just benchmark`. These commands do not exist yet and must not be reported as passing.

Targets: Linux x86_64 desktop reference, Android arm64-v8a device; Android emulator can check UI/bridge, not certify actual NPU/energy behavior. Build prerequisites and exact JDK/NDK/SDK/Rust/Python versions are to be measured and pinned by WORK-0001. Inspect available toolchains rather than assuming the current execution host has Android support.

Bootstrap acceptance: reproducible workspace build, minimal CLI status, Kotlin→Rust status call, isolated check/test jobs, dependency locks. This can be built without pretending the privacy backend exists: unsupported network AI operations fail closed.

Future CI: rustfmt, Clippy, tests with --locked; Gradle lint/JVM/device tests; protobuf compatibility; DB crash-recovery; malformed message handling; backend policy denial; conformance and independent test peer. Run only checks relevant to the patch. Physical-device thermal/energy tests are separately labeled.
