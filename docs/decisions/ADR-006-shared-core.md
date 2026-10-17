# ADR-006 — Rust shared core with Kotlin UI and CLI

Status: accepted design baseline, 2026-10-17.

## Decision
Core owns policy/state; concrete adapters assembled in runtime. Independent test peer required beyond same-core Android/CLI.

## Consequences
Implementation must reference this decision and provide evidence. Changes require a superseding ADR, never silent rewriting of history.

Canonical detail: [docs/architecture/overview.md](../../docs/architecture/overview.md).
