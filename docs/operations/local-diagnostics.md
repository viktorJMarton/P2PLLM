# Local diagnostic CLI

WORK-0010 implements a persistent local status-diagnostic ledger. It performs
no inference or remote execution. The existing `status` JSON contract is
unchanged. Build with Rust 1.88.0 and a C compiler for bundled SQLite:

```text
cargo build --locked -p p2p-node-cli
p2p-node status
p2p-node diagnostic run <database-path> smoke-001
p2p-node jobs list <database-path>
p2p-node jobs recover <database-path> --offline
```

Use the built `target/debug/p2p-node` (`p2p-node.exe` on Windows), or
`cargo run --locked -p p2p-node-cli --` before command arguments. The database
parent directory must already exist. Keep local runtime databases outside
tracked source, for example in a new directory under `.artifacts/runtime/`.
Do not use personal information in task IDs. Repeating a diagnostic ID returns
its persisted terminal state; it does not run it again. Use a fresh ID for a
new observation. Success means the local status diagnostic completed, even if
AI and network capabilities are unavailable; it never means AI work succeeded.

Each operation acquires an OS file lock before opening the database. Stop all
other runtime owners before `recover --offline`; the CLI also rejects a held
ownership lock. Only running diagnostics become interrupted, in one transaction.
The storage port itself requires its caller to enforce lifecycle ownership.
Never remove the sibling .owner.lock file while clients might be using it,
or access the same database via hard links or externally replaced path aliases.
Database IO failures are explicit errors; no in-memory success fallback exists.

```text
python tools/run_checks.py --profile storage-local --work-id WORK-0010 --run-id local-001 --bundle
```

The narrower storage-local profile tests local metadata transactions, competing
writers, process exit before commit, restart recovery and CLI integration. The
full `storage` gate stays unavailable because model-file activation and its
recovery protocol do not exist. `rust` additionally checks formatting/Clippy and
the whole workspace. Physical-device and Linux evidence are recorded separately.

## Android local diagnostic v1 (WORK-0014)

The0.2.0 app can start the same local core diagnostic and view saved results.
UniFFI open_local_diagnostics returns a process-owned LocalDiagnostics object;
run uses an idempotent ID, list reads a bounded SQL page (1..50, offset<=10000).
The database is filesDir/local-diagnostics.sqlite3, never shared external storage.
Shared storage::lease replaces the former CLI-only lock implementation.
First exclusive native runtime initialization recovers abandoned Running tasks;
reopening Activity/wrapper reuses the owner and cannot recover active work.
Stable typed errors replace raw SQL/path messages. RecoveryRequired tells the
user to fully stop/restart the Android app, not endlessly retry the same ID.
The UI never manually calls recovery or labels diagnostic success AI success.
See [the exact contract](../../work/WORK-0014-android-persistent-diagnostic/contract.md).
