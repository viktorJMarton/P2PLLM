# Storage department handoff

- work_id: WORK-0010
- run_id: run-20261022-storage-01
- department / role: desktop-node / local storage implementation
- journal_owner: primary agent
- integration_owner / recipient: primary agent
- status: in_progress; combined build/checks and independent review pending
- branch / absolute worktree path: work/local-storage-android-shell; C:/Users/Viktor/repos/P2PLLM
- baseline_revision: 341be683d1da785fac2d9ad0e2b75b22e396f2ca
- source_revision: uncommitted
- owned_paths: crates/node-core/src/tasks.rs; tasks module export in crates/node-core/src/lib.rs; crates/storage-sqlite/; this handoff
- shared_contract_owner: core/storage agent coordinated API before CLI implementation

## Inputs and scope

Read AGENTS.md, WORK-0010 brief, PRODUCT.md, TECHNOLOGY.md, architecture overview
and interfaces, threat model, desktop-node role and department workflow. Targets
REQ-005, REQ-006 and REQ-009. Ownership is disjoint within the shared checkout.

Implemented a core metadata-only TaskStore port and concrete SQLite adapter.
IDs permit 1..64 ASCII alphanumeric, underscore or hyphen characters. Core has
no SQLite dependency. Creation is idempotent at any current state; legal
transitions compare expected versions; terminal states are immutable.

SQLite schema version 1 uses transactional migration and rejects unsupported
future versions. Immediate write transactions serialize writers; state changes
and append-only event inserts commit together. Foreign keys and synchronous
FULL are enabled. Exact rusqlite dependency is =0.32.1 with bundled SQLite;
workspace/lockfile composition belongs to integration owner.

Recovery is never automatic on open. Caller must ensure exclusive lifecycle
ownership before recover_interrupted; it marks all running diagnostics
interrupted within one transaction. SQLite write locks alone cannot prove
that an external process has abandoned a task. No process-owner detection or
distributed lease is claimed. These local ledger events contain sequence,
task ID, state and version only, and do not implement the planned asynchronous
runtime event contract with timestamps/run correlation.

## Acceptance evidence

Observed Windows sandbox command:

`C:/Users/Viktor/.rustup/toolchains/1.88.0-x86_64-pc-windows-msvc/bin/rustfmt.exe --edition 2021 crates/node-core/src/tasks.rs crates/storage-sqlite/src/lib.rs`

Exit 0. The initial `rustup run 1.88.0 rustfmt ...` invocation exited 1 because
the rustup shim attempted to remove rustup-init.exe and received access denied;
direct installed-toolchain rustfmt was used instead, without changing toolchain.

Implemented tests (execution evidence to be supplied by integration owner):

- Bounded ID validation and lifecycle state pairs.
- Idempotent create in running and succeeded states; ordered event versions.
- Independent database connections reject stale expected versions.
- Injected event insertion failure rolls back creation and transition.
- Recovery failure after an earlier task update rolls back all recovered tasks.
- Reopen retains running state until explicit recovery, which is idempotent.
- Failed migration rolls back tables/version; future schema is unchanged.

Reopen tests simulate owner interruption; they are not power-loss measurements,
OS process-kill tests or filesystem-plus-model activation recovery evidence.

## Package provenance

No package, signing, publication or independent profile run performed by this
department. Integration owner runs common profiles on stable combined source.

## Independent review

Independent correctness/security reviewer requested; latest source snapshot
review and commit-bound acceptance remain pending. Implementer is not reviewer.

## Integration and next action

Parent integrates Cargo workspace/lockfile and actual status diagnostic CLI,
then runs applicable profiles and records exact combined-source evidence.
No network jobs, model execution, private computation or file activation is
implemented or authorized by this SQLite ledger.
