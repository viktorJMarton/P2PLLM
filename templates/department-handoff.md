# Department handoff

- work_id:
- run_id:
- department / role:
- primary persona / role document:
- journal_owner:
- integration_owner / recipient:
- status: proposed / in_progress / blocked / verified
- branch / absolute worktree path:
- baseline_revision:
- source_revision: exact commit, or explicitly uncommitted
- dirty_state / reviewed_snapshot_reference:
- owned_paths / shared_contract_owner:

## Inputs and scope

Brief, acceptance criteria, REQ/RFC/ADR links, applicable role and dependencies.
State implemented scope separately from planned capabilities.

## Changes and decisions

Changed paths, behavior, contract versions, concise rationale, compatibility and
recovery implications. Identify fixture-backed UI or simulated behavior.

## Acceptance evidence

| Criterion | Profile / exact command | Environment / versions | Exit code / outcome | Report / artifact reference |
| --- | --- | --- | --- | --- |
| | | | | |

Record observed outcomes only. Name missing tools, backend, credentials or
hardware as blockers. Distinguish docs validation, host tests, emulator tests and
physical-device measurements; no code or tests run means exactly that.

## Package provenance

Output directory, report, bundle and SHA-256 manifest references; manifest
verification outcome. Explicitly state whether outputs are debug/release and
signed/unsigned when applicable. Packaging alone does not authorize publication.
Exclude secrets and user/training data.

## Independent review

Reviewer, exact reviewed commit or uncommitted snapshot, findings, resolutions
and pending commit-bound review. State required security/privacy review. The
author and pair partner cannot be the sole reviewer. Record any later changes
that require renewed review/checks.

## Integration and next action

Sprint closure / GitHub synchronization (mandatory for successful closure):
- intended remote / development branch:
- final local commit / independent review reference:
- push command / exit code / outcome:
- remote branch SHA / verification command / match:
- closure: pending / pushed and verified; concrete blocker if pending:

Dependency readiness, shared API coordination, combined-revision checks still
required, open risks/blockers, next owner and concrete next action. Only the
journal owner consolidates this handoff into the work journal.

## Journal meeting and lesson references
Own agent journal / last iteration / last meeting revision:
Peer journals actually read / unanswered question IDs / respondents:
At least 5 concrete meeting questions, actual response/decision references:
Applicable agents/MEMORY.md lessons / new evidence-backed lesson proposed:
Independent next work / shared work blocked / next responsible agent:
Apply [the 3-iteration meeting contract](../docs/operations/agent-meetings.md).
Do not infer meeting, review or owner approval from silence.
