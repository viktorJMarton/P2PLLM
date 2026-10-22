# WORK-0010 independent correctness and security review

Reviewer: /root/product_review (not implementer/pair). Run: RUN-20261022-INDEPENDENT-REVIEW.
Observed 2026-10-22 17:07 UTC. Source is uncommitted on baseline
341be683d1da785fac2d9ad0e2b75b22e396f2ca. Commit-bound acceptance remains pending.

## Findings and disposition

No blocking source correctness/security finding in the bounded local diagnostic
ledger snapshot below. This is not release/privacy approval.

- Resolved during review: recovery must exclude another active lifecycle owner,
  beyond SQLite transaction ownership. `crates/node-cli/src/lease.rs` acquires a
  persistent sibling-file exclusive fs2 lock before opening SQLite; all shipped
  diagnostic/list/recovery paths retain that guard through their operations.
  Canonical path resolution merges ordinary relative/symlink aliases; lock file
  is not deleted during normal operation. This is cooperative process ownership,
  not a hostile local-user boundary. Raw adapter users must satisfy the explicit
  exclusive-lifecycle precondition; hardlink aliases are unsupported.
- Adapter uses immediate transactions for creation, state/event transitions,
  migration and whole recovery. Expected-version comparison occurs inside the
  write transaction. Legal transitions and terminal states live in core without
  SQLite dependencies. Version/ID decoding fails explicitly. Newer schemas are
  rejected; migration failure rolls back DDL and schema version.
- SQL values are parameterized; identifiers are bounded ASCII, rejecting SQL/JSON
  metacharacters. No arbitrary payload, prompt, tensor, credential or peer data
  column exists. No remote execution or privacy backend is introduced.
- Nonblocking follow-up: `TaskStore::list`, adapter events and recovery currently
  materialize all records. Introduce pagination/retention before exposing this
  interface to high-volume producers; this diagnostic-only slice has no remote
  producer. ASCII bounds do not prove an ID is nonpersonal; caller contract applies.

## Observed verification and limits

Inspected root-run `.artifacts/checks/WORK-0010/rust-local-001/rust/report.json`:
Rust 1.88.0 format/Clippy/workspace tests/build each exited 0, Windows 11,
Python 3.12.0, frozen uncommitted source fingerprint
030e77633a190c715e433ea9ded51636267c2ddb3172797a5f40436cbec662e4.
This report is historical to subsequent documentation edits.

Reviewer directly reran already-built test executables in Windows PowerShell:

- `target/debug/deps/p2p_storage_sqlite-4d4fc389cfd8ece8.exe --test-threads=1`: exit 0, 9 passed (including one helper that is a no-op without its child-only environment variable).
- `target/debug/deps/cli-87e2b0b28206f1c6.exe`: exit 0, 3 passed.
- `target/debug/deps/p2p_node-8a36882a1fda2539.exe`: exit 0, 3 passed.

These exercise synchronized concurrent writers, stale CAS, event-failure rollback,
whole recovery rollback, migration rollback, future-schema rejection, child process
exit before commit without Rust destructors, explicit reopen recovery, CLI
idempotence, invalid-ID side effects and lease exclusion/release. Reviewer did not
independently rebuild these binaries; source/build linkage relies on root profile
evidence and needs the final combined run. Process-exit injection is not power-loss,
filesystem/model activation or distributed ACID proof. No AI inference implemented.

## Exact-byte SHA-256 reviewed source

| Path | SHA-256 |
| --- | --- |
| Cargo.toml | 0D0CADFB26AD7A3506AF87E56E78A3713B297F18ED85B61F85B5BB7C29A7E491 |
| Cargo.lock | 905C7D6B8EDD2E55CC4300F4E685FF02BE302E38C1F0AFC7742CF1B1A5B656F1 |
| crates/node-core/src/lib.rs | 9BF29E907C2E042FFBEDEB974AA56D93594B2BC5DB822EFB86D77CE1953DD68F |
| crates/node-core/src/tasks.rs | 2B55BAB4441213FA98CF6DC27C66FFE07A615D104A91DA4865282AABE95679AA |
| crates/storage-sqlite/Cargo.toml | 8A43F392B637A3130248C3870156426623CDBD5158BC2ECC8299B27088C45828 |
| crates/storage-sqlite/src/lib.rs | 8AD478BF1C15415014F44DC247E0CD5E857C347794572E1A783F87265F8A7E89 |
| crates/node-cli/Cargo.toml | 2275055F3611BE2E335C0E606D1D49D3F75F23015300E513BA7E2DFB7AF015FB |
| crates/node-cli/src/main.rs | 37E96A0291E30A5AC4EDF1A9B7CCA944751BDF39318FDA95DE0790CADB2C37C0 |
| crates/node-cli/src/diagnostics.rs | D127402C0EB56D490F7822BBC911069FCAF5F5FD174495B162FBC53204E0B39E |
| crates/node-cli/src/lease.rs | 230ACBEE95849F7CB9E2AACA9929532C14D258800C9E36248AB22F4B917DF810 |
| crates/node-cli/tests/cli.rs | 9402EA7EC6B8733FE85BFFB672B45F6EABAE0256210936F6BA21779116BAF0F4 |

Coordinator owns final frozen checks, source/contract evidence and commit;
reviewer must confirm final commit paths match this snapshot before acceptance.
