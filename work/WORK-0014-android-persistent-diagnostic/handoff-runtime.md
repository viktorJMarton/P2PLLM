# Persistent local diagnostic runtime handoff

- WORK / run: WORK-0014 / run-20261023-android-diagnostic-01.
- Agent / persona: sqlite-layer / desktop-node, Pragmatic Rust systems engineer.
- Integration/journal owner: primary. Independent reviewer: product_review requested.
- Branch/workspace: work/WORK-0002-phone-baseline; C:/Users/Viktor/repos/P2PLLM.
- Baseline: ba6b116f15567ba0469040ff1b73542e57d7f71c; source uncommitted.
- Status: host implementation/checks delivered; independent review, Android
  build/device acceptance and final commit/push remain primary-owned.

## Owned source and behavior

crates/android-bridge adds LocalDiagnostics object/open/run/list with accepted
[contract](contract.md), stable payload-free errors and record schema1. A strong
process registry keeps at most16 canonical database owners alive until OS exit;
same-path Activity reopen clones existing Arc. try_lock contention returns Busy.
Initialization under registry ownership acquires exclusive shared fs2 lifecycle
lease, opens/migrates SQLite and recovers Running only before publishing the new
runtime. There is no public Activity recovery/cancel/close API or RAM fallback.

Shared lease moved from node-cli/src/lease.rs (deleted) into storage-sqlite/src/lease.rs;
CLI still acquires it for complete operations. fs2 dependency moved to storage,
bridge adds storage dependency. Primary updated Cargo.lock. Core tasks.rs now
owns start/finish/run local diagnostic rules reused by CLI/bridge. Core stays
independent of SQLite. Diagnostic success is a NodeStatus schema check and
committed state transitions, never inference, contribution or network success.

Storage pagination uses parameterized SQL LIMIT/OFFSET, at most51 decoded rows
to return50 plus continuation, ID ascending. Offset ceiling10000 can stop before
all records; pages are not a multi-call stable snapshot. No total-count claim.
Core CAS/idempotence, terminal immutability and transactional event append remain.

## Observed verification

Environment Windows11, installed Rust1.88.0 MSVC, bundled rusqlite=0.32.1,
fs2=0.4.3. Direct toolchain cargo/rustfmt paths used under
C:/Users/Viktor/.rustup/toolchains/1.88.0-x86_64-pc-windows-msvc/bin;
RUSTC points to matching installed rustc. Source uncommitted and other agents
own disjoint changes, so these targeted results are not a final frozen profile.

| Command | Exit / result |
| --- | --- |
| `cargo test --locked -p p2p-android-bridge -p p2p-storage-sqlite -p p2p-node-core -p p2p-node-cli` first attempt | 1;3 bridge ownership assertions failed because Windows lock contention was classified Unavailable |
| Same four-package command after precise fs2 OS-error mapping | 0;28 test entries pass, including2 helpers |
| Owned-files `rustfmt --edition 2021 ...` | 0 |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | 0 |
| `cargo test --locked -p p2p-android-bridge` after actual exported-registry assertion in kill child | 0;9 entries pass |

The Windows fix uses pinned upstream fs2::lock_contended_error raw OS mapping;
other errors still StorageUnavailable. Initial test failures remain history.
Tests include idempotent persisted result/event count, bounded ordered paging
including explicit cutoff, Busy/external ownership, same-owner reopen while
Running, corrupt storage, unexpected Running=>RecoveryRequired, registry cap,
and real parent-issued OS child kill after committed Running. Next exclusive
owner recovers Interrupted once/version2/events3. The private cfg(test) hook is
not exported and no UI crash/cancel control exists.

This is not Android process/device, power-loss, filesystem/model activation,
private compute, full storage or release evidence. No APK/package/signed release
was built or published by this department.

Frozen implementation reference (exact-byte SHA256, before later review fixes):

- bridge/src/diagnostics.rs: 040E053F2FA0BDF0103F3E2670FFF0DAACE7B4D243D9C9FDBB8FF929C0DF9456.
- storage-sqlite/src/lease.rs: 2CEC112E9A9F68872B0FAD3A2E0E4A93DF6115B5881D9AC8F51121B697C4ADD0.
- storage-sqlite/src/lib.rs: 4A27EDA2EF8F6559F9C974684F8A4AF9861098BC67A8D74D245172BED2F6ABA8.
- node-core/src/tasks.rs: D3512F1EDC6D0CB66C71F95A5B05AF6CAFA8D1E0FEAD5470914DBE407ED737D0.

## Journal meeting and lesson references

[Own journal](../agent-journals/sqlite-layer.md) iterations5/6 and actual meeting6
have peer receipts and at least5 concrete questions under
[meeting rules](../../docs/operations/agent-meetings.md). Actual primary/runtime
API agreement precedes coding. LSN-005 lifecycle ownership, LSN-004 freeze before
final evidence and LSN-006 no device claim from host tests apply. Original
storage implementer is not its independent reviewer even after persona changes.

## Integration and sprint closure

Primary owns Kotlin, generated bindings, shared contract/docs, native build,
device evidence and final common checks. Open RUNTIME-Q1..Q5 cover independent
registry/lease review, generated API/executor use, device lifecycle, pagination
wording and final exact-source acceptance. Ordinary canonical aliases supported;
hardlink/external replacement remain excluded per ADR-010. App must supply its
private filesDir path and trusted filesystem; this API is not a local hostile
process sandbox. No schema/profile approval or cryptographic gate is changed.

Primary must record final commit, successful development-branch push and observed
remote SHA after required review/checks. This handoff does not claim completed
sprint, merge, publication or final independent approval.
