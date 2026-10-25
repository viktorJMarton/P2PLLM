# WORK-0004 — Authenticated session and independent peer

Status: in_progress

A host-only synthetic loopback lab slice has real Rust/Python
TCP interoperability evidence in handoff-loopback-lab.md; authenticated
cross-platform sessions and the acceptance cases below remain open.
Requirements: REQ-002, REQ-005, REQ-007
Roles: protocol, android, desktop-node, testing, security
Dependencies: WORK-0001 host Rust/toolchain scaffold; full Android acceptance is not required for independent host-only work

## Objective and scope
Implement RFC-0001 and bounded schema; synthetic deterministic tasks; separately written Python test peer for interoperability.

## Acceptance
Handshake/version/error/cancel/replay/size tests; no secure-channel claim upgraded to private inference.

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
