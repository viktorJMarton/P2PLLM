# Android operator app (WORK-0001/0011/0014/0015)

The Kotlin/Compose app uses the generated UniFFI0.28.3 bridge for status and a
persisted local diagnostic. Version0.2.0/code2 adds a real start button on overview
and jobs, actual result/history, typed errors and bounded paging. Rust owns SQLite
under Android filesDir, the process lifecycle lock and first-owner recovery;
Activity recreation does not recover live work. All native/storage calls run
off the main thread. WORK-0015 version0.3.0/code3 adds the bounded offline AI tab through ADR-013; it does not connect to peers.
WORK-0014 records Kotlin/native ARM64 debug APK build on Windows. Host crash/
ownership tests are not Android device/UI validation; device acceptance remains
separate. WORK-0002 phone inventory/helper proof is not model inference evidence.
The application dependency graph is pinned in `app/gradle.lockfile`.

## Desktop build prerequisites

Windows users can use the [pinned developer environment](../docs/operations/development-environment.md):
`python tools/dev_env.py install --accept-sdk-license`, then `doctor` and
`android-build`. The existing Linux build script and colleague's Termux policy
remain separate routes; do not infer one host's result for all platforms.

- JDK 17, Android SDK platform 35, build tools 35.0.0 and NDK
  27.0.12077973 (the documented default for AGP 8.9.0).
- Rust 1.88.0 with `aarch64-linux-android` target.
- `cargo-ndk` 3.5.4: `cargo install cargo-ndk --version 3.5.4 --locked`.
- Set `ANDROID_HOME` for the SDK and `ANDROID_NDK_HOME` for that NDK.

From the repository root run `just build-android`. This cross-compiles
`libp2p_android_bridge.so` into `app/src/main/jniLibs/arm64-v8a/` and
then runs `android/gradlew :app:assembleDebug`. The shared library and
APK are ignored by Git. `android/gradlew` pins Gradle 8.11.1 and its
distribution checksum; the wrapper JAR SHA-256 is
`2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046`.

When changing the Rust UniFFI API, regenerate the checked-in Kotlin binding
with the pinned generator:

```sh
bash tools/regenerate-android-bindings.sh
```

Observed Windows equivalent (all UniFFI types are in this workspace; use a new
output directory, then copy the generated Kotlin file with UTF-8/LF):

```text
cargo build --locked -p p2p-android-bridge
cargo run --locked -p p2p-android-bridge --bin uniffi-bindgen -- generate --library target/debug/p2p_android_bridge.dll --language kotlin --config crates/android-bridge/uniffi.toml --metadata-no-deps --no-format --out-dir .artifacts/bindings/NEW
```

Generated file: uniffi/p2p_android_bridge/p2p_android_bridge.kt under that output;
destination is app/src/main/java/uniffi/p2p_android_bridge/p2p_android_bridge.kt.
Both native library and generated bindings must come from the same bridge API.
The checked-in uniffi.toml selects Android-aware object cleanup: SystemCleaner
only on API34+, existing JNA fallback below that. Do not use JVM-only Cleaner
unconditionally or raise minSdk/suppress lint to hide an incompatible binding.

The device smoke result requires a supported desktop SDK installation.
The Gradle dependency lock was generated with `./gradlew :app:dependencies
--write-locks` on JDK 17.
The 35.0.0 Linux build tools archive was inspected on this aarch64 proot:
its `aapt2` executable is x86-64, so an APK build on this host is not
supported by that official package. A generated binding on Linux does
not prove the Android call works.

## Offline question/answer build (WORK-0015)

`python tools/build_android.py` now first runs verified JNI/model preparation,
then the existing Rust/Android build. Windows prerequisite: pinned ExecuTorch
source/static runtime from WORK-0002, approved NDK, export venv/wheelhouse and
recovered hash-verified PTE. Missing inputs block packaging; there is no automatic
model/runtime upgrade. The new preparation route is Windows-specific; other
host support is unverified. Direct Gradle packaging also checks payload hashes
and required ARM64 libraries/notices, preventing an empty AI APK.

The debug APK bundles about480MB of public pinned model/tokenizer data, with
component notices. First use copies/verifies assets in app-private no-backup
storage; partial copies are discarded/retried, and both hashes precede inference.
Questions/responses remain in process memory. Single worker survives Activity
recreation; backgrounding cancels and waits for the current native operation.
Stop does not imply immediate interruption of model load/prefill. Input<=1024
UTF-8 bytes; output<=128 new tokens/16384bytes. No network permission.

The test-only platform instrumentation needs no external test library:
`gradlew :app:assembleDebugAndroidTest`, then install app and test APK and run
`adb shell am instrument -w org.p2pai.app.test/org.p2pai.app.LocalInferenceSmokeInstrumentation`.
After an actual force-stop, repeat with `-e mode restart` before the component.
It emits only flags/counts/static failure codes. Compilation is not device
acceptance; see WORK-0015 evidence for actual results and remaining limits.
