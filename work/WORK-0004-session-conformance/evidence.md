# WORK-0004 evidence

The entries below cover only the public synthetic host lab. There is no model
benchmark or authenticated/private-compute security evidence.

## Bounded concurrent host sessions, 2026-10-25

`run-20261025-protocol-concurrency-03`, Windows 11, Rust 1.88.0 and Python
3.12.0, baseline `602bd638bd6f07e38dfed282dfa37b30b6b3754b`.
Protocol owner's `cargo test -p p2p-protocol-session --offline` passed 3/3;
`cargo fmt --all`, scoped Clippy with `-D warnings`, and peer-bin build all
exited 0. Rebuilt peer SHA-256:
`78f5b4fa0d454841d430326a65733d3c39e82098eaf23ea5be362d029cce3ae1`.
Separate Python interop author ran the real-process suite with both peer and
client binary paths set; 14/14 exited 0 in 0.663 seconds. Two new cases
confirmed second-result progress with a HELLO-confirmed held first client,
and eight active held clients causing immediate ninth close, followed by
successful replacement after releasing a slot. The 14 include one earlier
primary-authored CLI subprocess case. Test source SHA-256:
`1e0b3fd22fcc6637f0d426c24369e8e2ce24df62da8acdafb67359a30418f580`.
No throughput, Linux/Android, authentication or privacy measurement follows.
Combined checks and latest-commit review remain pending at this entry.

Primary reran all 14 real-process Python interop cases, exit 0 in 0.390
seconds. Common `docs`, `workflow` and `rust` profiles under
`protocol-concurrency-20261025-001` each passed exit 0 on identical before/
after source fingerprint
`cb9c1592b5123cffc131aee412eb1ee4dfd4d53e657495f0a3a9086744dcb222`.
Docs package ran 829 checks plus agent flow; workflow ran 99 tests with two
environment skips; Rust workspace fmt, Clippy, tests and desktop build passed.
Reports: `.artifacts/checks/WORK-0004/protocol-concurrency-20261025-001/`.
Final meeting/evidence append needs refreshed docs/inventory before commit.

## Manual Rust client follow-up, 2026-10-25

`run-20261025-protocol-cli-02` on Windows 11: `rustup run 1.88.0 cargo build
-p p2p-protocol-session --bins --locked --offline` exit 0. With
`P2P_LAB_PEER_BIN=target/debug/p2p-lab-peer.exe` and
`P2P_LAB_CLIENT_BIN=target/debug/p2p-lab-client.exe`, explicit Python 3.12
`-m unittest discover -s tests/interop -p 'test_*.py' -v` passed 12/12 in
0.472 seconds, exit 0. The new process case observed the client returning
`529` for `23` through an actual loopback socket and rejecting `192.0.2.1:9`
before connect. The WindowsApps Python alias failed exit 1 before tests;
the explicit Python312 executable worked. Source is uncommitted at this point.

Common profile receipts for `protocol-cli-20261025-001` all passed, exit 0,
on identical source fingerprint
`9c3b53158da21d53ec6e9f998ccdbedfb42e5032b2a2a04a9fb33405312a0896`:
`docs` package 829 checks and agent flow; `workflow` 99 tests with two
environment skips; `rust` workspace fmt, Clippy, tests and desktop build.
Reports: `.artifacts/checks/WORK-0004/protocol-cli-20261025-001/`.

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
