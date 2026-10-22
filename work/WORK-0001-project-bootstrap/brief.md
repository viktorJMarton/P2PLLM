# WORK-0001 — Buildable repository and CI foundation

Status: in_progress
Requirements: REQ-001, REQ-007, REQ-009
Roles: architecture, android, desktop-node, testing
Dependencies: none

## Objective and scope
Create Cargo workspace and minimal Kotlin/UniFFI status call; CLI status; pin measured toolchains; CI; all unsupported private operations fail closed.

## Acceptance
Desktop executable and Android bridge build with documented commands; schema/package checks pass; no claim of working AI network.

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
