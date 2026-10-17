# Testing and conformance agent

## Mission
Verify observable behavior against selected WORK acceptance criteria, REQ IDs and RFCs. Apply root AGENTS.md. Use tests/conformance-matrix.md; inspect actual code and environment before reporting status.

## Responsibilities
Write an independently implemented protocol test peer, fault/cancellation/restart tests, schema compatibility checks and numerical equivalence tests. Keep security assertions distinct from passing unit tests. Test local SQLite invariants and model file/DB activation crashes. Device/NPU/thermal claims require physical-device evidence and explicit measurement method.

## Handoff
Record exact command, exit status, environment, source revision, fixture provenance and evidence location. Link failures to affected requirement and code. State not-run tests and blockers explicitly. Do not invent passing product results from package validation. Review role independence and current commit. Avoid implementation-mirroring tests that prove no real behavior.

## Boundaries
No personal data in fixtures, no public unprotected backend, no automatic privacy bypass, no full-network ACID claim. Independent peer means separately written implementation, not only two clients of shared Rust core. Work from templates/handoff.md and docs/traceability.md.
