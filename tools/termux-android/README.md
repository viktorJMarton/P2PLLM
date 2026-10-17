# Termux Android ARM64 build

Build host: Termux / PROOT Ubuntu ARM64
Branch: build/termux-android-arm64

## Toolchain

```text
aarch64
rustc 1.88.0 (6b00bc388 2025-06-23)
cargo 1.88.0 (873a06493 2025-05-10)
openjdk version "17.0.17" 2025-10-21
cargo-ndk 3.5.4
Android SDK: 35
Android Build Tools: 35.0.0
Android NDK: 27.0.12077973
Gradle: 8.11.1
```

## Notes

- Android SDK and NDK binaries are not committed.
- x86-64 tools require QEMU wrappers.
- Wrapper paths assume the documented Ubuntu layout.
- External dependencies must be installed separately.
- This branch is not a production release.
