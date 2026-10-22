# WORK-0010 evidence

Run run-20261022-storage-01; implementation and checks in progress.
Record actual commands/environment/commit/results here; no product claims yet.

## run-20261022-storage-01 observed execution

Environment: Windows 11 x86_64, Visual Studio 2022 C toolchain, installed Rust
1.88.0 (6b00bc388), bundled SQLite via rusqlite =0.32.1, fs2 =0.4.3,
Python 3.12.0 for the smoke driver. Cargo.lock records exact dependencies.
Source was uncommitted on work/local-storage-android-shell for these commands.

| Command | Exit | Observation |
| --- | ---: | --- |
| `rustup toolchain install 1.88.0 --profile minimal --component rustfmt --component clippy` | 0 | Pinned toolchain installed; rustup also attempted self-update; one delegated shim invocation later failed access-denied and used installed direct rustfmt instead |
| `cargo test --workspace` initial dependency resolution | 0 | 13 initial Rust tests passed; exact lockfile updated with SQLite/locking dependencies |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` initial | 101 | manual_range_contains lint; corrected schema version check to inclusive range |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` after correction | 0 | No warnings |
| `python tools/run_checks.py --profile rust --work-id WORK-0010 --run-id rust-local-001 --bundle` | 0 | fmt, Clippy, locked tests and CLI build pass; 19 tests (including crash child helper); stable source fingerprint and CLI bundle |
| Python subprocess/sqlite3/msvcrt smoke against actual `target/debug/p2p-node.exe` | 0 | Diagnostic succeeded at version2; repeated ID identical; independent list retained record, exactly3 events; external process lock rejected recovery; recovery worked after release |

Smoke database: `.artifacts/runtime/work10-smoke-001/node.db`, sanitized IDs only.
Bundled report/binary: `.artifacts/checks/WORK-0010/rust-local-001/rust/`.
The process-crash regression exits a child without transaction destructors before
commit, verifies rollback, then explicitly recovers the persisted running task.
It does not simulate power loss or filesystem/model activation.

## Review and acceptance limits

Independent product_review inspected early core/storage/UI and requested an
enforced CLI lifecycle lock; fs2 guard was added and tests passed. The reviewer
then hit the agent usage limit before final source/commit/security confirmation.
Final independent review remains required; this work is not marked verified.
Linux reference-device, Android SQLite integration, network/AI execution and
model-file recovery were not tested or implemented in this slice.

## Superseding review state, 2026-10-22

Independent product-review resumed, inspected final bounded source/security
paths and directly reran15 existing test-binary entries successfully. Its
review.md records exact source hashes and no blocking bounded-scope finding.
All original SQL journal questions have actual peer responses; no meeting
replaces the pending exact-commit/fresh-profile confirmation. The earlier
usage-limit interruption remains history rather than the current review status.

## Final local implementation checks

Windows11/Rust1.88, push-final-001: rust profile19 test entries, fmt/Clippy/build
passed; storage-local18 test entries/build passed, both exit0. Reports/bundles:
.artifacts/checks/WORK-0013/push-final-001/{rust,storage-local}/. Stable snapshot
was uncommitted; subsequent edits are MD only. Final commit review/push tracked
in WORK-0013; device/private AI/model activation are not claimed.
