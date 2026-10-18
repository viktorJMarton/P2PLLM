#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BRANCH="build/termux-android-arm64"
export ANDROID_HOME="/opt/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_NDK_HOME="$ANDROID_HOME/ndk/27.0.12077973"
export CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER="/opt/android-build/bin/android-clang"
export PATH="$HOME/.cargo/bin:$PATH"
export GRADLE_USER_HOME="${GRADLE_USER_HOME:-$HOME/.gradle}"
LOG_DIR="$ROOT/.build-logs"
mkdir -p "$LOG_DIR"
die() { echo "ERROR: $*" >&2; exit 1; }
cd "$ROOT"
[[ "$(git branch --show-current)" == "$BRANCH" ]] || die "Refusing build outside $BRANCH."
[[ -x "$CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER" ]] || die "Run bash tools/termux-android/bootstrap.sh first."
[[ -x /opt/android-build/bin/aapt2 ]] || die "AAPT2 wrapper missing; run bootstrap.sh."
[[ -d "$ANDROID_NDK_HOME" ]] || die "Android NDK not installed."
[[ -f "$ANDROID_HOME/platforms/android-35/android.jar" ]] || die "Android SDK 35 missing."
[[ -f /opt/amd64-libs/usr/lib/x86_64-linux-gnu/libz.so.1 ]] || die "x86_64 zlib missing."
[[ -x android/gradlew ]] || die "Gradle wrapper missing."
grep -q 'android.aapt2FromMavenOverride=/opt/android-build/bin/aapt2' android/gradle.properties || die "Expected AAPT2 override missing."
grep -q 'keepDebugSymbols' android/app/build.gradle.kts || die "Expected native symbol packaging setting missing."
command -v rustc >/dev/null || die "Rust missing."
command -v java >/dev/null || die "Java missing."

echo "Building ARM64 Rust bridge..."
cargo build --release --locked --target aarch64-linux-android -p p2p-android-bridge \
  2>&1 | tee "$LOG_DIR/rust-android.log"
SO="$ROOT/target/aarch64-linux-android/release/libp2p_android_bridge.so"
[[ -s "$SO" ]] || die "Rust bridge output missing."
file "$SO"
install -d "$ROOT/android/app/src/main/jniLibs/arm64-v8a"
install -m 644 "$SO" "$ROOT/android/app/src/main/jniLibs/arm64-v8a/libp2p_android_bridge.so"

echo "Assembling Android debug APK..."
(cd android && ./gradlew --no-daemon --max-workers=1 :app:assembleDebug) \
  2>&1 | tee "$LOG_DIR/gradle-android.log"
APK="$ROOT/android/app/build/outputs/apk/debug/app-debug.apk"
[[ -s "$APK" ]] || die "APK not found."
python3 "$ROOT/tools/termux-android/archive-apk.py" --apk "$APK" --allow-existing\necho "SUCCESS: $APK"
ls -lh "$APK"
if [[ "${COPY_TO_DOWNLOADS:-0}" == "1" ]]; then
  [[ -d /sdcard/Download && -w /sdcard/Download ]] || die "/sdcard/Download is not writable in this proot."
  cp "$APK" /sdcard/Download/P2PLLM-debug.apk
  echo "Copied to /sdcard/Download/P2PLLM-debug.apk"
fi
