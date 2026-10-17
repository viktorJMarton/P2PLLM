# RFC-0003 — cooperative adapter learning (draft)

Learning round negotiates base composition, adapter layout, optimizer/update semantics, participant conditions and approved privacy profile. Train local inputs under owner enrollment policy; never turn arbitrary received answers into training truth. Raw records/personal adapters do not leave the node by default.

Protected aggregation produces a candidate, not mandatory active weights. Individual updates must not be exposed contrary to profile. Secure aggregation, DP, Byzantine robustness and provenance address different threats; document the combination and limits. Honest-majority assumptions require a membership story in an open Sybil-prone network.

Validate candidate on held-out tasks and regression suite. Local approval activates an immutable composition with crash-safe rollback. Exact LoRA aggregation semantics must be specified; naive independent factor averaging is not assumed equivalent to averaging delta weights. Do not assume Android can train every exported ExecuTorch graph.

MVP must include useful private shared learning, with numerical/quality metrics, DP accounting if claimed, leakage/collusion analysis and independent review.
