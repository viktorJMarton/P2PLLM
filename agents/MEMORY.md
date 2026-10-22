# Evidence-backed project memory

Read applicable lessons on start/resume and at each 3-iteration meeting.
See [meeting procedure](../docs/operations/agent-meetings.md). These lessons
record observed project experience; they do not claim model training or new
privacy guarantees. Preserve evidence and propose contract changes explicitly.

## LSN-001 — Provision prerequisites instead of repeating missing-tool blockers

Observed: Android build stopped because Java was never provisioned, while Rust
was installed. [WORK-0011 evidence](../work/WORK-0011-android-local-shell/evidence.md).
Correction: [WORK-0012](../work/WORK-0012-development-environment/brief.md) owns
pinned bootstrap, activation and doctor checks. Ordinary authorized setup is
autonomous; legal owner choices are explicit and scoped. SDK license approval
for the four pinned packages was received; do not ask it again in this session.
Enforcement: bootstrap/doctor must precede capability claims; implementation and
Android compile are still in progress, so this lesson is not marked solved.

## LSN-002 — Source identity must survive Windows/Linux checkout conversion

Observed: raw CRLF hashes and Windows path separators invalidated the source
inventory. [WORK-0009 journal](../work/WORK-0009-department-workflows/journal.md).
Correction: tools/source_inventory.py uses utf8-lf-v1 and slash paths; artifacts
remain exact bytes. Enforcement: tests/test_source_inventory.py and docs profile.

## LSN-003 — Timeout must stop descendant build processes

Observed: killing only the parent left a child writing after timeout.
[Independent review](../work/WORK-0009-department-workflows/review.md).
Correction: Windows Job Objects / POSIX process groups in tools/run_checks.py.
Enforcement: descendant cleanup regression in tests/test_run_checks.py.
Scope: trusted build harness; not a hostile-process security sandbox.

## LSN-004 — Freeze source writers before claiming a reproducible check

Observed: a reviewer updating an MD file changed the fingerprint during tests;
the complete run failed even though its test subprocess passed.
[Evidence](../work/WORK-0009-department-workflows/evidence.md).
Correction: coordinate writer freeze, then run final checks with a fresh run ID.
Enforcement: runner compares before/after source fingerprints and HEAD.

## LSN-005 — Recovery needs lifecycle ownership, not just a DB write transaction

Observed: reviewer identified recovery could interrupt another active owner
between transaction commits. [WORK-0010 evidence](../work/WORK-0010-local-task-storage/evidence.md).
Correction: CLI fs2 ownership guard; core port documents caller responsibility.
Enforcement: CLI lock test, subprocess smoke, SQL concurrency/process-exit tests.
Final independent/security review remains pending; no approval is inferred.

## LSN-006 — Inactive agents and source delivery are not completed review/build

Observed: parallel agents delivered code but usage limits interrupted final
review; Android source had no successful compile. [UI evidence](../work/WORK-0011-android-local-shell/evidence.md).
Correction: preserve handoffs, assign a review successor, name missing evidence.
Enforcement: final exact-revision review and Android build remain required.
An unavailable respondent leaves meeting questions open; it never approves them.

## LSN-007 — A successful sprint closure includes the GitHub push

Observed: the owner explicitly required development-branch pushes at every
successful sprint closure, including the current MD change (2026-10-22).
Evidence: AGENTS.md mandatory sprint closure section and GOVERNANCE.md standing
authorization; current execution is logged under WORK-0013.
Correction: commit, push the assigned development branch and verify remote SHA;
do not repeatedly ask for authorization already granted for this scope.
Enforcement: department-workflow.md closure procedure and mandatory handoff
fields. Failed push means pending closure; no force-push/default-branch merge.
