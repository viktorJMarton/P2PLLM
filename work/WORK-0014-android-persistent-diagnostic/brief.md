# WORK-0014 — Observable persistent Android local diagnostic

Status: verified
Run: run-20261023-android-diagnostic-01.
Requirements: REQ-005, REQ-006, REQ-009.
Roles: desktop-node, android, testing, pr-review. Baseline ba6b116 with ongoing
WORK-0002 tooling changes; no uncommitted source is represented by HEAD alone.

## Owner request and priority

On2026-10-23 owner reports refreshed appearance but no visible activity and
authorizes continued development. Deliver one real user action and durable
result, while the assigned model researcher retains WORK-0002 first priority.
No complete task engine, AI inference or network capability is claimed here.

## Acceptance

- Start local diagnostic from overview/jobs, with visible in-flight/success/error.
- Rust owns SQLite under Android private filesDir; typed stable bridge contract
  in contract.md, bounded SQL list and idempotent request IDs.
- One process runtime owns lease, initialization recovery and serialized work;
  rotation/reopening Activity never interrupts live tasks or triggers recovery.
- A process-killed persisted Running diagnostic is deterministically tested,
  then observed interrupted on the next exclusive runtime initialization.
- Saved records survive process restart; no fake success or silent RAM fallback.
- Independent code/security review, applicable host checks, native Android APK,
  actual-device evidence where available; missing device acceptance stays open.
- Versioned APK plus checksum, commit and observed checks delivered to existing
  owner Drive hierarchy; successful checkpoint commit/push remotely verified.

## Coordination and autonomous continuation

Use the [agent meeting contract](../../docs/operations/agent-meetings.md): own
persona/journal, no more than3 iterations, at least5 concrete peer questions and
actual responses. Routine reversible work in this brief is autonomous. The
runtime and UI owners have separate paths; primary owns brief, contract, logs,
integration/bindings/build metadata. Privacy and model runtime gates stay intact.
