# WORK-0012 — Provisioned and repeatable development environment

Status: in_progress
Requirements: REQ-009, REQ-007
Roles: orchestrator, testing, android
Dependencies: WORK-0009; supports WORK-0010 and WORK-0011

## Objective
Provision the actual Windows developer host with pinned JDK 17, Android SDK35,
build-tools35 and NDK27.0.12077973, while preserving Rust1.88 and Gradle wrapper.
Provide a repeatable bootstrap/activation/doctor path, shared versioned cache
support for separate worktrees and CI, checksums and observed build evidence.

## Acceptance
Exact archive URLs/hashes locked; no silent major tool upgrades. Project-local
activation does not rewrite global PATH. Missing SDK license owner acceptance
is explicit, never fabricated. Common checks run inside the provisioned
environment; Kotlin compile/build failures are addressed with actual evidence.
Existing product changes and colleague Termux policy are preserved.

## Coordination and autonomous continuation
Use the [agent meeting contract](../../docs/operations/agent-meetings.md): your
own MD journal, at most 3 iterations between peer-journal meetings, at least 5
concrete questions with respondents and real response references. Routine
reversible implementation/research within this brief is autonomous. Missing
hardware/review blocks only acceptance and dependent capabilities; keep useful
independent work moving. Do not infer approval from unavailable peers.
