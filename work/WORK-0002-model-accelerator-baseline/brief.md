# WORK-0002 — Pinned Qwen and accelerator inventory

Status: not_started
Requirements: REQ-001, REQ-010
Roles: qwen-research-deputy, research, android, learning, mathematical-modeling
Dependencies: WORK-0001

## Objective and scope
Resolve immutable Qwen3-0.6B revision, evaluate 1.7B candidate; PyTorch reference and ExecuTorch export; CPU/GPU/NPU smoke tests and memory/thermal profile.

## Acceptance
Model manifest with revision/hash/license; reproducible reference/export comparisons; report unsupported operators and actual hardware.

## Verification
Follow relevant RFCs and tests/conformance-matrix.md. Capture exact command, environment, exit status and evidence. Any unavailable device/backend is a blocker. Review binds to exact code revision. Apply root AGENTS.md.

## Boundaries
No external publication, license selection, arbitrary remote code, personal-data lab fixtures, automatic weak privacy fallback or fabricated passing results. Record research uncertainty explicitly.
