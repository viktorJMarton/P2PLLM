# WORK-0009 — Reproducible department checks and evidence packages

Status: verified
Verification scope: original local WORK-0009 implementation and review at341be68.
Later policy/tooling edits are tracked and rechecked under WORK-0012/0013;
this historical status does not preapprove future changes or invent meetings.
Requirements: REQ-009, REQ-007
Roles: orchestrator, testing, pr-review
Dependencies: WORK-0001 (existing scaffold only; Android completion not claimed)

## Objective and scope
Provide a common local/CI entry point for department-specific checks, with
explicit unavailable capabilities, commit-bound reports and bounded artifact
packaging. Define isolated work ownership and integration gates. Preserve the
colleague's Android/Termux work; no merge or publication is part of this task.

## Acceptance
- Versioned profiles distinguish implemented checks from future storage,
  interoperability, device and privacy gates.
- A standard-library Python runner records commands, exit codes, environment,
  source revision and dirty state; a missing prerequisite never passes.
- Evidence bundles contain the report and explicitly declared build outputs,
  with SHA-256 provenance; no broad workspace/log/credential collection.
- Behavioral tests cover failure, unavailability and package integrity.
- Documentation, CI entry point, source manifest and evidence are current.
- Independent review covers the final changed source snapshot; commit-bound
  review remains pending if no implementation commit is created.

## Boundaries
No AI, privacy, Android-device or transactional implementation claim. The runner
does not provision toolchains/SDKs, sign, upload, merge or install a background
service. Build tools may restore pinned dependencies/Gradle distributions on a
provisioned host; this workflow is not an offline-build guarantee.
Each department receives a separate WORK/branch/worktree before product changes.

## Coordination and autonomous continuation
Use the [agent meeting contract](../../docs/operations/agent-meetings.md): your
own MD journal, at most 3 iterations between peer-journal meetings, at least 5
concrete questions with respondents and real response references. Routine
reversible implementation/research within this brief is autonomous. Missing
hardware/review blocks only acceptance and dependent capabilities; keep useful
independent work moving. Do not infer approval from unavailable peers.
