# WORK-0003 — Privacy threat model and primitive feasibility

Status: not_started
Requirements: REQ-003, REQ-004
Roles: security, mathematical-modeling, research, protocol
Dependencies: WORK-0001 host Rust/toolchain scaffold; full Android acceptance is not required for independent host-only work

## Objective and scope
Compare exact malicious-secure MPC and FHE primitive profiles. Define who may collude, setup assumptions and bounded outputs. No arbitrary independent-peer assumption.

## Acceptance
Assumption-bound privacy profile proposal; numerical/cost measurements; Android feasibility; explicit rejection/selection ADR; qualified review before approval.

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
