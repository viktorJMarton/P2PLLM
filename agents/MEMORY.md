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

## LSN-008 - Console redirection does not prevent in-process payload file logs

Observed2026-10-23: pinned ExecuTorch export builder unconditionally logs example
inputs/kwargs; Hydra INFO FileHandler persisted tensor representations although
worker stdout/stderr went to devnull. Initial0B observation became stale;
post-cleanup two known logs were4435bytes. WORK-0002 evidence/journal contain the
explicit dated correction and sanitized containment receipt. Known raw logs
were removed; this is not a claim that no payload ever persisted.

Correction implemented in tools/export_qwen.py: logging protections precede model
imports; Hydra logging/metadata is disabled.19 targeted host tests passed, also
independently rerun; actual installed Hydra/builder no-model canary probe passed
including reconfiguration and late/direct handlers. Keep exception diagnostics to
bounded types/static frames, never messages/locals/source or tensor formatting.
Preserve immutable pins, serialization/network and child-job cleanup guards.
Affected independent review resolved the specific Python/Hydra logging blocker;
prior execution no-blocker was withdrawn when the hazard was found. No actual
model export was rerun after this repair; PTE/numerical/backend/phone gates remain.
Enforcement owner: WORK-0002 exporter implementer and independent reviewer;
Python logging guards do not establish an OS/native-code confidentiality sandbox.

## LSN-009 - Verify the executed packaging guard, not just its declaration

WORK-0015 first APK build succeeded without executing its payload guard because
Kotlin Gradle task Spec resolved project.name. Explicit it.name fixes the hook.
Actual negative assemble rejected missing model; positive common Android build
executed the guard. Evidence: WORK-0015 evidence.md and payload-guard-001 receipt.
Enforcement: exact asset hashes, required native/notices, observed task execution.

## LSN-010 - Native source bytes and packaged bytes can differ reproducibly

AGP stripped the already-built JNI library again. Initial strict audit correctly
stopped; pinned NDK llvm-strip --strip-unneeded reproduced exact APK bytes.
Record distinct source and packaged hashes plus tool/argv/exit and byte equality;
never waive unexplained mismatches. WORK-0015 strip-provenance-002 and portable
observations bind final bytes. ELF headers alone are not provenance/security.

## LSN-011 - Pin and measure the model prompt framing

A closed thinking prefix alone did not satisfy the public exact-answer fixture.
Same-pin A72 comparison supported literal /no_think suffix. Both owners agreed
before code; golden native template regression and rebuilt actual app passed
unchanged strict assertion. Preserve prior failure; a small answer pass is not
full numerical/quality/backend/privacy acceptance. WORK-0015 evidence.md.
