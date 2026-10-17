# Android source bootstrap (WORK-0001)

This is a Kotlin/Compose status screen wired to the generated UniFFI
`nodeStatus()` function. It does not run inference or connect to peers.
The checked-in Kotlin binding was generated from the host Rust bridge using
UniFFI 0.28.3. A matching Android arm64 shared library is still required
for an APK. No Android build or device run has been verified.
The application dependency graph is pinned in `app/gradle.lockfile`.

## Desktop build prerequisites

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

The device smoke result requires a supported desktop SDK installation.
The Gradle dependency lock was generated with `./gradlew :app:dependencies
--write-locks` on JDK 17.
The 35.0.0 Linux build tools archive was inspected on this aarch64 proot:
its `aapt2` executable is x86-64, so an APK build on this host is not
supported by that official package. A generated binding on Linux does
not prove the Android call works.
