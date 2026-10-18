#!/usr/bin/env bash
set -Eeuo pipefail

# Run inside Termux proot-distro Ubuntu as root, not in Termux's native shell.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SDK="/opt/android-sdk"
NDK_VERSION="27.0.12077973"
TOOL_BIN="/opt/android-build/bin"
LIB_DIR="/opt/amd64-libs/usr/lib/x86_64-linux-gnu"
BOOTSTRAP_DIR="$ROOT/tools/termux-android"
export DEBIAN_FRONTEND=noninteractive
export ANDROID_HOME="$SDK"
export ANDROID_SDK_ROOT="$SDK"
export ANDROID_NDK_HOME="$SDK/ndk/$NDK_VERSION"
export PATH="$SDK/cmdline-tools/latest/bin:$HOME/.cargo/bin:$PATH"

die() { echo "ERROR: $*" >&2; exit 1; }
[[ "$(id -u)" == 0 ]] || die "Start in proot Ubuntu as root."
[[ "$(uname -m)" == "aarch64" ]] || die "Expected aarch64 host."
[[ -f /etc/os-release ]] || die "Linux distribution not detected."
[[ -f "$ROOT/android/gradlew" ]] || die "Run from the repository's tools/termux-android directory."
[[ "$(git -C "$ROOT" branch --show-current)" == "build/termux-android-arm64" ]] || die "Checkout build/termux-android-arm64 first."
[[ -e /usr/x86_64-linux-gnu/lib/ld-linux-x86-64.so.2 || -e /usr/x86_64-linux-gnu/ld-linux-x86-64.so.2 ]] || echo "NOTE: verify x86_64 cross runtime loader if QEMU fails."

echo "Checking prerequisites..."
for tool in java rustc cargo rustup python3 qemu-x86_64 unzip wget dpkg-deb; do
  command -v "$tool" >/dev/null || die "Missing $tool. Install this prerequisite in Ubuntu first (APT repositories must be configured for arm64)."
done
java -version 2>&1 | grep -q 'version "17\.' || die "JDK 17 required."
rustc --version | grep -q '^rustc 1\.88\.0 ' || die "Rust 1.88.0 required; run rustup toolchain install 1.88.0."
[[ -x "$SDK/cmdline-tools/latest/bin/sdkmanager" ]] || die "Missing sdkmanager at $SDK/cmdline-tools/latest/bin. Install Android commandline tools before rerunning."
[[ -f "$LIB_DIR/libz.so.1" ]] || {
  echo "Missing $LIB_DIR/libz.so.1"
  echo "Enable valid amd64 Ubuntu package indexes, then run:"
  echo "  mkdir -p /opt/amd64-libs && cd /opt/amd64-libs"
  echo "  apt download zlib1g:amd64 && dpkg-deb -x zlib1g_*_amd64.deb ."
  die "x86_64 zlib must be supplied independently (do not modify APT sources automatically)."
}

echo "Installing SDK packages (if absent)..."
sdkmanager --install "platforms;android-35" "build-tools;35.0.0" "ndk;$NDK_VERSION"
rustup target add aarch64-linux-android
if ! cargo ndk --version 2>/dev/null | grep -q '3.5.4'; then
  cargo install cargo-ndk --version 3.5.4 --locked
fi
install -d "$TOOL_BIN"
install -m 755 "$BOOTSTRAP_DIR/android-clang" "$TOOL_BIN/android-clang"
install -m 755 "$BOOTSTRAP_DIR/aapt2" "$TOOL_BIN/aapt2"

[[ -x "$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin/ld.lld" ]] || die "NDK linker missing."
[[ -f "$SDK/platforms/android-35/android.jar" ]] || die "Android platform 35 missing."
"$TOOL_BIN/aapt2" version
echo "Bootstrap checks finished. Build with: bash tools/termux-android/build.sh"
