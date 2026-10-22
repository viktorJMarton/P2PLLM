# WORK-0007 — Android operator UI and contribution lifecycle

Status: not_started
Requirements: REQ-005, REQ-006
Roles: android, architecture, security, testing
Dependencies: WORK-0001, WORK-0004

## Objective and scope
Implement independent roles, five screens, network kill switch; foreground experimental mode; then background constraints on real phone.

## Acceptance
Stop/cancel/resource withdrawal works; user-visible contribution; no unsupported always-on claim; no camera permission just for NPU.

## Verification
Follow relevant RFCs and tests/conformance-matrix.md. Capture exact command, environment, exit status and evidence. Any unavailable device/backend is a blocker. Review binds to exact code revision. Apply root AGENTS.md.

## Boundaries
No external publication, license selection, arbitrary remote code, personal-data lab fixtures, automatic weak privacy fallback or fabricated passing results. Record research uncertainty explicitly.

## Coordination and autonomous continuation
Use the [agent meeting contract](../../docs/operations/agent-meetings.md): your
own MD journal, at most 3 iterations between peer-journal meetings, at least 5
concrete questions with respondents and real response references. Routine
reversible implementation/research within this brief is autonomous. Missing
hardware/review blocks only acceptance and dependent capabilities; keep useful
independent work moving. Do not infer approval from unavailable peers.
