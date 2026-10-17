#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

if [[ -z "${ANDROID_NDK_HOME:-}" || ! -d "$ANDROID_NDK_HOME" ]]; then
  echo "ANDROID_NDK_HOME must point to a local Android NDK installation" >&2
  exit 2
fi
if ! command -v cargo-ndk >/dev/null 2>&1; then
  echo "Install cargo-ndk 3.5.4 before building Android" >&2
  exit 2
fi
if [[ "$(cargo ndk --version)" != *"3.5.4"* ]]; then
  echo "Expected cargo-ndk 3.5.4" >&2
  exit 2
fi
if [[ ! -x android/gradlew ]]; then
  echo "Android Gradle wrapper is missing or not executable" >&2
  exit 2
fi

cargo ndk -t arm64-v8a -o android/app/src/main/jniLibs build --release --locked -p p2p-android-bridge
cd android
./gradlew --no-daemon :app:assembleDebug
