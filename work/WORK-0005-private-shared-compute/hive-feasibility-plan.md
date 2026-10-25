# Cross-platform hive: research synthesis and next bounded milestone

Status: proposal, 2026-10-25. WORK-0005 / run-20261025-hive-research-01.
Owner: primary; persona: Accountable delivery coordinator. This document is
uncommitted until its recorded source checkpoint. No networked AI, approved
privacy profile, secure backend or cooperative learning implementation follows
from this plan. It preserves [ADR-001](../../docs/decisions/ADR-001-ecosystem-scope.md)
and [ADR-003](../../docs/decisions/ADR-003-privacy-gate.md).

The product is an Android **and** desktop P2P node system. The phone app is one
interface and one possible compute contributor. Current code provides a bounded
local Android inference path and local Rust status/task/storage slices. There is
no implemented peer transport or distributed scheduler; WORK-0004 and WORK-0005
are still not started. The current published model has a reproduced answer
quality regression, and the corrected candidate is too large and slow to ship.
See [WORK-0002 checkpoint](../WORK-0002-model-accelerator-baseline/handoff-quality-checkpoint.md).

This synthesis uses the actual [research handoff](../WORK-0003-privacy-primitive-selection/handoff-hive-research-20261025.md)
and [mathematical handoff](../WORK-0003-privacy-primitive-selection/handoff-hive-math-20261025.md).
Their source links, assumptions and counterexamples are part of this proposal.

## Architecture choice to test first

Build a common Rust node lifecycle around versioned, authenticated sessions,
locally validated capability offers, bounded task reservations, cancellation
and status. Android and Linux desktop use the same protocol and policy contracts.
An independently implemented test peer is required for interoperability.
This is the first testable hive slice under [WORK-0004](../WORK-0004-session-conformance/brief.md),
not an inference or privacy milestone. Start with public synthetic tasks. The
peer is never trusted merely because it advertises a model, resources or a
privacy flag. Phone contribution is a revocable lease; Android process and
background restrictions must be measured on the target device.

For a *private* request, the local policy must reject remote routing until an
approved profile covers the exact operation, inputs, outputs, implementation,
participants and failure behavior. TLS/QUIC does not hide plaintext from the
computing peer. Ordinary layer/tensor splitting likewise reveals intermediate
state and stays in a public/synthetic lab. Petals demonstrates a possible
resource-sharing mechanism under its own conditions, not privacy or A72/Qwen
performance for this product. Desktop availability and bandwidth are hypotheses
to measure, not grounds to grant it trust.

The protected path remains the [WORK-0003 experiment](../WORK-0003-privacy-primitive-selection/experiment-plan.md):
first a pinned synthetic exact projection with real malicious-secure backend
preprocessing, fault/abort tests and both-party costs; then qualified review of
the explicit threat/profile assumptions. A primitive pass may inform a useful
bounded Qwen subgraph under WORK-0005. It does not establish full-model private
inference. WORK-0006 separately needs exact adapter-delta aggregation semantics,
protected round, quality/poisoning/dropout evidence and crash-safe activation.

## Measurements that decide whether peers help

For each same-contract local/remote pair, record end-to-end latency from offer
through checked result, local and peer compute, queue, connection/setup, model
distribution amortized over a stated job count, upload/download bytes and rates,
network rounds/RTT, cryptographic preprocessing, checks, retries/aborts, owner
CPU, peak memory and energy when instrumented. Record direct versus relay and
Wi-Fi versus mobile-data paths; report failures as well as p50/p95. Do not add
overlapping stages twice: use the measured critical path. Compare equal model,
operation, output/security policy and answer-quality criteria. The existing
privacy plan sets a stronger offload-utility gate: paired evidence must support
both lower owner CPU and lower complete latency, with uncertainty excluding
parity. A missing energy measurement leaves the energy claim open.

The mathematical handoff's examples illustrate why measurement matters:
40 sequential tokens crossing one peer boundary at an assumed 50 ms RTT incur
about 2 seconds of round-trip floor; a 2.55 GB candidate model would take at
least about 34 minutes over an assumed 10 Mbit/s before overhead; three truly
independent 95%-available required peers give only about 85.74% all-party
availability. These are scenarios, not observed network or reliability results.

## Parallel work and next sprint boundary

| Workstream | Immediate bounded deliverable | Gate before stronger claim |
| --- | --- | --- |
| WORK-0002 local model | Compact export, strict reproducible English/Hungarian quality and measured A72 resources | Useful output and device runtime evidence; current candidate is unshipped. |
| WORK-0004 protocol | Two nodes, one independently implemented, authenticate/version/negotiate, run public synthetic task, cancel/replay/reconnect under bounded resources | Interoperability and security review; no private-input routing. |
| WORK-0003 privacy | Execute the preregistered exact projection with pinned real backend on host, then target Android/Linux; measure full setup/cost/fault behavior | Qualified review and local approved profile for exact operation; currently none. |
| WORK-0005 shared compute | After dependencies, integrate one useful protected subgraph with measured local/remote parity and cost | Exact operation coverage, approved profile, quality, resource and dropout gates. |
| WORK-0006 learning | Specify versioned LoRA delta semantics and synthetic protected round design | Actual protected update, utility, poisoning/dropout and recovery evidence. |

The next *network* sprint should be the WORK-0004 synthetic two-node session
and task lifecycle. Its acceptance is a real authenticated connection and a
bounded synthetic task between Android and desktop or, if phone support is not
yet ready, Linux-to-Linux explicitly labelled host-only. Include peer discovery
path, direct/relay observation, version mismatch, duplicate/replay rejection,
cancellation, expiry and safe resource withdrawal. It can proceed alongside
WORK-0002 model quality and WORK-0003 backend experiments because these own
different contracts and files. A desktop peer and an Android peer must be
measured before cross-platform support is claimed.

The implementation owner should first turn [RFC-0001](../../docs/rfcs/RFC-0001-session.md)
and [RFC-0002](../../docs/rfcs/RFC-0002-compute.md) into a small versioned schema
plus independently testable conformance cases. Research and mathematics may
refine scheduling thresholds after actual RTT, goodput, backend and dropout
measurements. No accepted PRODUCT/TECHNOLOGY/ADR change is proposed silently.

## Open decisions and evidence limit

The exact privacy profile/collusion bound, secure backend revision/parameters,
which useful Qwen subgraph to protect, mobile process availability, and any
model runtime switch remain open. The independent reviewer may check this
document's consistency and sources; that review is not qualified cryptographic
approval. The research/math handoffs used official documentation and original
papers, but no new distributed execution or human answer-quality rating ran.
