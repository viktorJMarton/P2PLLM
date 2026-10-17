# ADR-005 — Versioned base and locally accepted adapters

Status: accepted design baseline, 2026-10-17.

## Decision
No automatic global model updates. Sessions pin exact composition. Held-out evaluation and rollback required.

## Consequences
Implementation must reference this decision and provide evidence. Changes require a superseding ADR, never silent rewriting of history.

Canonical detail: [docs/models/update-lifecycle.md](../../docs/models/update-lifecycle.md).
