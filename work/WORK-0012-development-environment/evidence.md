# WORK-0012 evidence

Run run-20261022-environment-01. Windows x86_64. Provisioning in progress;
do not describe downloads as a verified Android environment before build checks.

## Observed JDK/SDK and Kotlin compilation

Windows x86_64; Microsoft OpenJDK17.0.20.1+1 (java -version confirmed), Gradle
wrapper8.11.1. SDK35 platform revision2, Build Tools35.0.0, Command-line Tools16.0
and NDK27.0.12077973 downloaded and checked against Google metadata SHA1/size,
then independently SHA256-pinned in config/development-windows.json. JDK archive
SHA256 matched Microsoft's published checksum. Owner approved exactly these SDK
packages/license through the explicit user response; no broader terms accepted.

Command (activated JAVA_HOME/ANDROID_HOME/ANDROID_NDK_HOME and cache-scoped
GRADLE_USER_HOME):

```text
android/gradlew.bat -p android --no-daemon :app:compileDebugKotlin
```

Exit 0: `BUILD SUCCESSFUL in 3m 28s`, 14 tasks executed, including
`:app:compileDebugKotlin`. Existing two-file Kotlin source compiled without
changes; native Android library/APK and device execution were not part of this
command. Gradle noted optional Platform-Tools not installed; that extra package
was not silently installed or license-approved.

## Native debug APK build

`python tools/dev_env.py android-build` completed with exit0: Rust release ARM64
bridge2m08s and Gradle assembleDebug1m51s (35 tasks,21 executed/14 up-to-date).
Initial APK was10161713 bytes, SHA256
56bbf7635780a586c2df67e6d2195ffb3cdd6b7bc5f0d108e2a5029860856d37;
ZIP inspection confirmed lib/arm64-v8a/libp2p_android_bridge.so. It also exposed
dependency libraries for ABIs with no Rust bridge. Added an arm64-v8a ABI filter
to match PRODUCT's supported Android target; final Android profile rebuild and
APK hash supersede this initial mixed-ABI artifact. No device execution inferred.

Earlier real provisioning failures were corrected: license raw-byte checksum
versus newline-normalized text; Windows relative slash batch invocation; bootstrap
argument parsing of --accept-sdk-license. Source helper now verifies archive/raw
license bytes and uses absolute Gradle path. No earlier failed report was rewritten.

## Final full Android profile

Activated Android profile push-final-002 passed, exit0: lintDebug, JVM task
(NO-SOURCE), native ARM64 bridge and assembleDebug. See WORK-0011/evidence.md
and .artifacts/checks/WORK-0011/push-final-002/android/. APK9329531 bytes,
SHA256e81af76449eda49a75229472128b3a310be11eacd734fd4227f287943b629bc1;
only arm64-v8a native libraries confirmed. Optional Platform-Tools not installed.
Sandbox push-final-001 failure retained; elevated rerun resolved access.
No emulator/device execution observed. Subsequent policy/evidence edits are MD only.
