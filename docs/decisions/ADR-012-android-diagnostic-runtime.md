# ADR-012 — Process-owned Android local diagnostic runtime

Status: accepted bounded implementation direction,2026-10-23; finalcheckpoint
review/checks recorded in WORK-0014. Supplements ADR-006/010, not a model runtime.

## Decision

Compose calls a version1 UniFFI LocalDiagnostics object on an executor. Rust
composes shared core diagnostic rules and SQLite under Android private filesDir.
Use the [WORK-0014 contract](../../work/WORK-0014-android-persistent-diagnostic/contract.md)
for exact records, bounded SQL page rules and typed sanitized errors.

Move the former CLI lifecycle lease into storage::lease so both composition
roots use the same exclusive ownership rule. A bounded strong native process
registry reuses owners across Activity lifetimes. Only first initialization
after exclusive lease acquisition recovers abandoned Running tasks; reopening
a screen never recovers live work. Fail closed on contention/storage errors.
Process restart is necessary for a stuck same-owner RecoveryRequired; do not
offer Activity-driven recovery or endless same-ID retry as a fix.

Core shares idempotent start/finish business rules, not FFI/platform types. CLI
and Android remain local diagnostic clients; neither success implies model or
peer work. Keep implementation dependency direction: core has no SQLite/Android
dependency; bridge is this bounded composition root. No async network engine,
filesystem/model activation, privacy profile, subscription or release acceptance.

## Evidence and consequences

WORK-0014 records host28testentries including deterministic OS child kill,
live-owner reopen, lease exclusion, once-only recovery and bounded pages.
Windowsfs2 contention needs raw lock_contended_error mapping; initial failures
are preserved. Kotlin/nativeAPK0.2.0 builds and actualSM-A725F action/persistence/
force-stop-relaunch evidence are separate from unobserved Androidactive-kill/
rotation-in-flight cases. No broad Android/runtime/privacy guarantee is inferred.
