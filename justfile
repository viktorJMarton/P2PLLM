set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

validate-package:
    python3 tools/validate_package.py

department-check profile work_id run_id:
    python3 tools/run_checks.py --profile '{{profile}}' --work-id '{{work_id}}' --run-id '{{run_id}}' --bundle

check:
    python3 tools/validate_package.py
    cargo fmt --all -- --check
    cargo clippy --workspace --all-targets --locked -- -D warnings

test:
    cargo test --workspace --locked

build-desktop:
    cargo build --locked -p p2p-node-cli

build-android:
    bash tools/build-android.sh

test-interop:
    @echo "Unavailable: independent protocol peer is WORK-0004" >&2
    @exit 2

benchmark:
    @echo "Unavailable: model/device benchmark is WORK-0002" >&2
    @exit 2
