# Documentation handoff

- work_id: WORK-0009
- run_id: RUN-20261022-WORK0009-DOCS
- role: workflow documentation
- recipient_role: orchestrator / integration owner
- status: in_progress
- source_revision: uncommitted; parent owner records final snapshot
- journal_owner: parent orchestrator

## Inputs read

AGENTS.md, this WORK brief, agents/orchestrator.md, work/INDEX.md,
docs/operations/ci-review.md, docs/architecture/overview.md,
docs/traceability.md, BUILD.md and templates/handoff.md.

## Observed result

Added the common department workflow and a department handoff template. They
define isolated ownership, API coordination, check/evidence packaging, department
gates, independent review and explicit unavailable capabilities. No product,
device, privacy or always-on automation capability is claimed.

## Changed paths

- docs/operations/department-workflow.md
- templates/department-handoff.md
- work/WORK-0009-department-workflows/handoff-docs.md

## Verification

Documentation written in the shared Windows PowerShell checkout with disjoint
ownership. Runner/profile implementation is owned by another agent. No runner or
product tests were run by this documentation role; parent integration must run
package/link validation after registering the new files in its owned manifest,
check profile command semantics and review the final snapshot.

`git diff --check -- <owned paths>` initially could not inspect the repository:
Git reported dubious ownership (combined command exit 1). Repeating the diff
command with command-scoped
`-c safe.directory=C:/Users/Viktor/repos/P2PLLM` exited 0, without changing global
Git configuration. This does not validate newly untracked files or product code.

## Open risks / next action

Independent review and applicable checks remain pending. The parent owner must
reconcile this prose against final runner behavior, record final source identity
and consolidate evidence serially. Android/Termux branch policy is preserved by
reference; it has not been integrated or overwritten here.
