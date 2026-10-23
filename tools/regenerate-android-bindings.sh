#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cargo build --locked -p p2p-android-bridge
cargo run --locked -p p2p-android-bridge --bin uniffi-bindgen -- \
  generate --library target/debug/libp2p_android_bridge.so \
  --language kotlin --config crates/android-bridge/uniffi.toml --out-dir "$tmp_dir"

python3 - "$tmp_dir/uniffi/p2p_android_bridge/p2p_android_bridge.kt" \
  "android/app/src/main/java/uniffi/p2p_android_bridge/p2p_android_bridge.kt" <<'PY'
from pathlib import Path
import sys

source, destination = (Path(path) for path in sys.argv[1:])
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    "\n".join(line.rstrip() for line in source.read_text().splitlines()).rstrip() + "\n"
)
PY
