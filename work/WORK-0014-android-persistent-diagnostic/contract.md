# Local diagnostic bridge contract v1

Run run-20261023-android-diagnostic-01; agreed primary/runtime via actual
2026-10-23 response. Primary is the UI implementer and acknowledges the same
contract before coding; separate UI subagent could not start due host thread cap.
This new API does not change existing node_status/BridgeStatus semantics.

## API

open_local_diagnostics(database_path:String) -> Result<Arc<LocalDiagnostics>,DiagnosticError>.
Object run(request_id:String) -> Result<DiagnosticRecord,DiagnosticError>.
Object list(limit:u32,offset:u32) -> Result<DiagnosticPage,DiagnosticError>.

Record: schema_version:u32=1, request_id:String, state:DiagnosticState, version:u64.
States: Queued, Running, Succeeded, Failed, Cancelled, Interrupted, matching core.
Page: schema_version:u32=1, records:Vec<DiagnosticRecord>, offset:u32,
next_offset:Option<u32>. SQL order request ID ASC, limit1..50, offset0..10000.
No unbounded read followed by in-memory truncation. Next offset exists only when
more records are observed and within bound; this is not a transaction-spanning
snapshot and concurrent changes can affect later pages. No total-count claim.
Stable errors: InvalidRequest, Busy, StorageUnavailable, RecoveryRequired,
Internal. Raw filesystem/SQLite/native diagnostics never cross to UI/logs.

## Ownership, recovery and execution

Android uses filesDir/local-diagnostics.sqlite3. Native calls, file operations and
binding initialization run on an executor, never UI/composition. Every run uses
a nonpersonal 1..64 ASCII identifier; same terminal ID returns stored result
without reexecution/events. Running repeat is RecoveryRequired, not success.
UI retains the pending ID for retry while that Activity instance is alive;
rotation/relaunch refreshes from durable records and does not pretend cancel.

Rust process registry holds strong Arc runtime handles across Activity recreation;
same canonical path returns same owner. At most16 registered databases; app uses
one. Shared fs2 lease guards full lifecycle. After first exclusive acquisition,
before exposing that runtime, interrupted recovery runs under ownership+mutex.
Later opens reusing runtime never recover. Only OS process exit releases owner;
no public Activity recovery/cancel method. Lock/mutex contention returns Busy.
Future file activation/distributed ownership remains outside this API.

Diagnostic success means local core schema inspection and committed task-state
transitions completed. AI/network availability can remain false. No model,
prompt, tensor, user identity or arbitrary payload is stored. User messages say
local diagnostic explicitly; success never means inference executed.

## Acceptance cases

1. Tap start: show in-flight, then actual terminal task ID/state/version.
2. Read stored records; reopening process uses same app-private database.
3. Repeat same ID: unchanged version/event count; new ID creates new diagnostic.
4. Recreate/open while live task is Running: same runtime, no recovery.
5. Deterministic host child-process kill after persisted Running, no destructors;
   next exclusive owner marks it Interrupted once, preserving terminal tasks.
6. Held ownership lock, invalid ID, DB I/O/schema failure, oversized list request:
   stable failure; no in-memory fallback or raw error text.
7. Host code/build evidence and actual Android process restart observations are
   separate. Absence of connected device cannot pass Android runtime acceptance.
