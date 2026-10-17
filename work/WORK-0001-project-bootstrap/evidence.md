# WORK-0001 evidence

## run-20261017-2217z (Ubuntu 25.04 proot, aarch64)

| Command | Exit | Observation |
|---|---:|---|
| `python3 tools/validate_package.py` before edits | 0 | 257 checks passed for original 109-file handoff |
| `cargo test --workspace` with Rust 1.84.1 | 101 | transitive crate required newer Cargo |
| `cargo test --workspace --locked` after Rust 1.88.0 and CLI fix | 0 | 2 Rust tests passed |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | 0 | no lint errors |
| `cargo build --workspace --locked` | 0 | CLI and host UniFFI library built |
| `cargo run --locked -p p2p-node-cli -- status` | 0 | JSON: network false; private compute/learning unavailable |
| `cargo run --locked -p p2p-android-bridge --bin uniffi-bindgen -- generate --library target/debug/libp2p_android_bridge.so --language kotlin --out-dir /tmp/p2p-ai-uniffi` | 0 | Kotlin `nodeStatus()` and `BridgeStatus` generated; ktlint formatting unavailable |
| `python3 tools/validate_package.py` after edits, before manifest refresh | 1 | expected manifest mismatch |
| `just test` | 0 | 2 Rust tests passed |
| `just build-desktop` | 0 | desktop CLI built |
| `just build-android` | 2 | `ANDROID_NDK_HOME` missing; no Android build |
| `sha256sum android/gradle/wrapper/gradle-wrapper.jar` | 0 | `2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046`, matches Gradle release |
| `android/gradlew --version` | 0 | Gradle 8.11.1 on JDK 17.0.17 |
| `android/gradlew --no-daemon :app:tasks --all` | 0 | Android Gradle project configured, tasks listed; no source compilation |
| `android/gradlew --no-daemon :app:dependencies --configuration debugRuntimeClasspath` | 0 | pinned Compose BOM, Kotlin and JNA dependencies resolved |
| `android/gradlew --no-daemon :app:dependencies --write-locks` | 0 | `android/app/gradle.lockfile` generated for resolvable configurations |
| `bash tools/regenerate-android-bindings.sh` | 0 | checked-in Kotlin binding reproducibly regenerated from the host Rust library |
| `sha1sum /tmp/p2p-build-tools-r35-linux.zip`; `unzip -p .../aapt2 \| file -` | 0 | official 35.0.0 build tools SHA-1 matched repository metadata; `aapt2` is x86-64 and cannot execute on aarch64 proot |
| `bash -n tools/build-android.sh android/gradlew` | 0 | shell syntax accepted |
| `python3 -m py_compile tools/validate_package.py tools/update_manifest.py` | 0 | Python syntax accepted |
| `python3 -c 'import xml.etree.ElementTree as E; E.parse("android/app/src/main/AndroidManifest.xml")'` | 0 | manifest XML parses |
| `just check` after source manifest refresh | 0 | 286 package/source checks, rustfmt and Clippy passed |
| `python3 tools/validate_package.py --write-report` | 0 | pre-binding-script snapshot: 289 checks passed, report in `PACKAGE-VALIDATION.json` |
| `just check; just test; just build-desktop; git diff --check` | 0 | local package/Rust checks, 2 tests and CLI build passed before final regeneration script |
| `python3 tools/validate_package.py --write-report; just check; just test; just build-desktop` | 0 | final source state: 290 validation checks and 2 Rust tests passed |

This evidence supports a host Rust bridge, not an Android APK or device call.
No model, NPU, libp2p session, private compute, or private learning test ran.
Source revision: baseline `68ef58f`; implementation uncommitted. The final
check results will be appended after the Android scaffold and manifest refresh.
