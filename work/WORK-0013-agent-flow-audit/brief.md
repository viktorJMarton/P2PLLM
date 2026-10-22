# WORK-0013 — Complete Markdown audit and agent coordination contract

Status: in_progress
Requirements: REQ-009
Roles: orchestrator, testing, pr-review
Dependencies: WORK-0009; preserves current WORK-0010–0012 progress

## Objective
Read every repository Markdown source in context, inventory findings, and
correct stale status, ambiguous ownership, excessive permission stops and agent
communication gaps. User decisions: each agent writes its own MD journal;
after at most three development iterations agents read one another's journals
and hold an asynchronous documented meeting with at least five concrete
questions. Joint decisions require actual peer responses, never invented consent.

## Acceptance
All MD files classified as reviewed with findings or rationale for no change.
Canonical rules linked from root, role guides and templates. Agent autonomy
applies to routine reversible work within accepted contracts; privacy, review,
legal/publication constraints remain accurately scoped. Meeting cadence,
question ownership, responses, escalation and continuation are explicit.
Executable policy checks exercise missing meetings/questions and receipt rules.
Historical evidence is preserved, corrections appended or clearly dated.

## Boundaries
No fictional agents, meetings, learned model weights, approvals or test results.
Parallel journals have separate writers. Agent unavailability is recorded;
unanswered shared decisions cannot be silently approved by timeout. Existing
code/environment work continues where it does not depend on open decisions.

## Coordination and autonomous continuation
Use the [agent meeting contract](../../docs/operations/agent-meetings.md): your
own MD journal, at most 3 iterations between peer-journal meetings, at least 5
concrete questions with respondents and real response references. Routine
reversible implementation/research within this brief is autonomous. Missing
hardware/review blocks only acceptance and dependent capabilities; keep useful
independent work moving. Do not infer approval from unavailable peers.
