# WORK-0011 — Android operator navigation and actual status

Status: in_progress
Requirements: REQ-005, REQ-009
Roles: android, testing, pr-review
Dependencies: existing WORK-0001 bridge; WORK-0009

## Objective
Implement the five product destinations in Kotlin/Compose. Load actual existing
UniFFI status outside composition and show loading/error/unavailable states.
Navigation and refresh work; unavailable model/network operations stay disabled.

## Acceptance
- Overview, AI session, jobs, models/learning and resources/privacy destinations.
- Actual bridge-backed state, explicit unavailable features, no sample metrics.
- Lifecycle-aware refresh, saved navigation, usable scroll/touch layout.
- No new build dependencies or changes to colleague-owned Gradle/Termux policy.
- Compile/test evidence when available; absent SDK/device remains a blocker.
- Independent review; this does not complete WORK-0007 network lifecycle scope.

## Coordination and autonomous continuation
Use the [agent meeting contract](../../docs/operations/agent-meetings.md): your
own MD journal, at most 3 iterations between peer-journal meetings, at least 5
concrete questions with respondents and real response references. Routine
reversible implementation/research within this brief is autonomous. Missing
hardware/review blocks only acceptance and dependent capabilities; keep useful
independent work moving. Do not infer approval from unavailable peers.
