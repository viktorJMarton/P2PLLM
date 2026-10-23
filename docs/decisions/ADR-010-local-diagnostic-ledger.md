# ADR-010 — Local diagnostic task ledger before network execution

Status: accepted implementation direction; independent final review pending.
Work: WORK-0010. Requirements: REQ-005, REQ-006, REQ-009.

2026-10-23 supplement: ADR-012/WORK-0014 adds a bounded Android composition root
and moves the shared lease to the storage adapter. The original initial-slice
description below is historical; Android now depends on the adapter for local
diagnostics only. Core remains independent and full model/network gates stayopen.

## Decision
Keep validated task IDs, lifecycle rules and the TaskStore port in node-core.
Implement storage in a separate p2p-storage-sqlite adapter. The CLI is the
composition root for this small synchronous diagnostic slice; core has no SQL
dependency. SQLite schema version 1 stores local status diagnostics only.

Use rusqlite =0.32.1 with bundled libsqlite3-sys 0.30.1, and fs2 =0.4.3 for
cooperative CLI process ownership. Cargo.lock pins the resolved dependency tree.
No platform SQLite installation is assumed. Bundled SQLite introduces a C
compiler prerequisite, including a supported Android cross-compiler for any
future Android integration. The Android bridge does not depend on this adapter.

Creation is idempotent by task ID. Immediate transactions atomically update
task state/version and append a metadata event. Migration is transactional;
newer schema versions fail. Explicit recovery marks running tasks interrupted
without changing queued or terminal tasks. Opening a store never recovers tasks.

The CLI holds a sibling .owner.lock file across its complete database operation,
including diagnostic execution and recovery. The file remains on disk; handle
closure releases the OS lock. It is not a distributed lease. All other users
must follow this ownership contract before calling recovery. Hard-linked or
externally replaced database/lock aliases are unsupported; local filesystem
integrity and a trusted owner are preconditions. SQLite cannot identify whether
another runtime's task is abandoned merely from a row marked running.

## Alternatives and scope
A core-to-rusqlite dependency would violate adapter boundaries. Automatic
recovery on open would interrupt another active owner. A full asynchronous
network job engine is deferred until its separate protocol/runtime contracts.

This ledger contains only IDs, states, versions and local event sequences. IDs
must be nonpersonal 1..64 ASCII letters/digits/underscore/hyphen. No prompt,
tensor, model content, identity key or arbitrary task payload is stored. It is
not the future correlated runtime-event subscription API.

SQLite rollback/process-exit tests do not prove power-loss behavior, model-file
activation consistency, private computation or distributed atomicity. Those
remain separate gates. No full WORK-0007/0008 completion follows from this ADR.
