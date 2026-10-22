# WORK-0010 — Durable local diagnostic task ledger

Status: in_progress
Requirements: REQ-005, REQ-006, REQ-009
Roles: desktop-node, testing, security, pr-review
Dependencies: WORK-0009; existing WORK-0001 scaffold

## Objective
Implement a Rust SQLite adapter behind a core storage port. Persist only bounded
local diagnostic task metadata and state events, without prompts or peer data.
Provide a CLI that actually records a local status diagnostic. No remote work.

## Acceptance
- Versioned schema migrations reject newer unsupported schemas.
- Task creation is idempotent; legal transitions use expected versions.
- Task/event changes commit atomically, with rollback, concurrency and reopen
  tests. Recovery explicitly marks running diagnostic tasks interrupted.
- Core does not depend on SQLite. Exact dependencies/lockfile and tests exist.
- CLI status remains compatible; diagnostic creation/run/list/recovery works.
- Independent correctness/security review and exact environment evidence.

## Boundaries
No distributed ACID, model activation, real AI execution or privacy proof.
No filesystem/model activation claim from SQLite-only tests. Diagnostic IDs are
bounded nonpersonal identifiers; no arbitrary task payloads or SQL from peers.

## Coordination and autonomous continuation
Use the [agent meeting contract](../../docs/operations/agent-meetings.md): your
own MD journal, at most 3 iterations between peer-journal meetings, at least 5
concrete questions with respondents and real response references. Routine
reversible implementation/research within this brief is autonomous. Missing
hardware/review blocks only acceptance and dependent capabilities; keep useful
independent work moving. Do not infer approval from unavailable peers.
