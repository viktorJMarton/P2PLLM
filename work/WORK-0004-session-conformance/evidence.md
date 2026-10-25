# WORK-0004 evidence

The entries below cover only the public synthetic host lab. There is no model
benchmark or authenticated/private-compute security evidence.

## Public synthetic loopback lab, 2026-10-25

Run `run-20261025-protocol-loopback-01`, Windows 11, Rust 1.88.0 and Python
3.12.0. Code and fixture changes are uncommitted until the final source
checkpoint. `cargo test -p p2p-protocol-session --offline` exit 0, three Rust
tests; `cargo fmt --all --check` exit 0; `cargo clippy -p
p2p-protocol-session --all-targets --offline -- -D warnings` exit 0;
`cargo build -p p2p-protocol-session --bin p2p-lab-peer --offline` exit 0.
No external dependency was added; Cargo.lock gained only the workspace package.

The independent peer command was `python -m unittest discover -s
tests/interop -p 'test_*.py' -v` with `P2P_LAB_PEER_BIN` set to the absolute
`target/debug/p2p-lab-peer.exe` path. It exited 0 with 11/11 real TCP cases
using fixed public synthetic IDs/numbers. The peer's last frozen test source
SHA-256 is `67422c01bd4422bb13c1b422f281a3715ef93b85f7596913770dd77359bb5430`;
the rebuilt executable SHA-256 observed by the testing agent is
`68f689ccf5e2c6b292e02323ed258d2e1656585584d8b7578b965c936309830c`.
Its journal contains the test chronology.
The Windows error on unread bytes after a rejected oversized frame may be
EOF or connection reset; the independent peer accepts either only after first
asserting the correct RESOURCE_LIMIT response. Its initial 8/9 run exposed this
harness assumption; a later first 11-case run exposed a fixture prefix error,
both repaired before the final 11/11 result.

The Rust owner separately sent one byte about every two seconds without LF;
Windows disconnected the session after about 30.11 seconds under the 30-second
absolute deadline. The first one-shot helper exited 1 because it did not
catch ConnectionAbortedError; the corrected helper exited 0. This is one
bounded host observation, not a production latency or availability study.
Provisional independent security review found no immediate parser blocker in
the public loopback scope; exact-commit review is pending. No model, phone,
cross-machine, authenticated transport or privacy backend execution occurred.
Final combined profile reports and commit/push receipts will be recorded after
writer freeze; an APK build is not applicable to this host-only change.
