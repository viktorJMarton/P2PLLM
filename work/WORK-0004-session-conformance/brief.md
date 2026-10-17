# WORK-0004 — Authenticated session and independent peer

Status: not_started
Requirements: REQ-002, REQ-005, REQ-007
Roles: protocol, android, desktop-node, testing, security
Dependencies: WORK-0001

## Objective and scope
Implement RFC-0001 and bounded schema; synthetic deterministic tasks; separately written Python test peer for interoperability.

## Acceptance
Handshake/version/error/cancel/replay/size tests; no secure-channel claim upgraded to private inference.

## Verification
Follow relevant RFCs and tests/conformance-matrix.md. Capture exact command, environment, exit status and evidence. Any unavailable device/backend is a blocker. Review binds to exact code revision. Apply root AGENTS.md.

## Boundaries
No external publication, license selection, arbitrary remote code, personal-data lab fixtures, automatic weak privacy fallback or fabricated passing results. Record research uncertainty explicitly.
