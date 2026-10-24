# WORK-0002 — Pinned Qwen and accelerator inventory

Status: in_progress
Three A72 inference observations are available in [phone-observations.json](phone-observations.json); numerical quality and actual-backend acceptance remain open.
Requirements: REQ-001, REQ-010
Roles: qwen-research-deputy, research, android, learning, mathematical-modeling
Dependencies: WORK-0001 host Rust/toolchain scaffold; full Android acceptance is not required for independent host-only work

## Objective and scope
Resolve immutable Qwen3-0.6B revision, evaluate 1.7B candidate; PyTorch reference and ExecuTorch export; CPU/GPU/NPU smoke tests and memory/thermal profile.

## Acceptance
Model manifest with revision/hash/license; reproducible reference/export comparisons; report unsupported operators and actual hardware.

## Current sprint owner decision, 2026-10-22
WORK-0002 has first claim on capacity; defer Android ledger integration before
reducing model measurement work. Target changed by owner from Honor400Pro to
Samsung Galaxy A72; read exact SKU, RAM and system build from the connected phone.
Begin with pinned Qwen3-0.6B CPU baseline, then assess 1.7B against measured budget.
Each report records immutable model/tokenizer revision and hashes, quantization,
export configuration, runtime revision/build and actual backend with evidence.
Measure model load, TTFT (inference start to first generated token), generation
throughput and process peak memory. Preserve every repeated trial and failures,
thermal context and ordering; do not claim cold OS cache from a fresh process.
No phone/backend/export availability means blocked measurement, not a benchmark.
See sprint-plan.md. Integration is deferred; WORK-0003 produces preregistration
only until a real secure-backend experiment is executed.

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
