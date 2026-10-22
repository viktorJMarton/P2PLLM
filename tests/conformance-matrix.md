# Conformance matrix

| ID | Case | Required outcome |
|---|---|---|
| TEST-001 | Exact supported composition | Result equivalent to pinned reference within defined tolerance |
| TEST-002 | Major protocol mismatch | Reject before task payload |
| TEST-003 | Model/tokenizer/adapter mismatch | Reject incompatible task |
| TEST-004 | Oversize frame/tensor | Reject before unbounded allocation |
| TEST-005 | Disconnect | Bounded timeout, defined recovery/restart |
| TEST-006 | Repeated same step/digest | No silent double KV advancement; cached/expired status |
| TEST-007 | Same step, different digest | STEP_CONFLICT |
| TEST-008 | Corrupt payload | Integrity failure; no implied correct-compute proof |
| TEST-009 | Unknown/unapproved privacy profile | Fail closed |
| TEST-010 | Peer claims privacy_verified | Ignored/rejected as authorization |
| TEST-011 | Remote executable payload | Reject outside operation allowlist |
| TEST-012 | Privacy backend absent | Local-only or explicit unavailable, no plaintext fallback |
| TEST-013 | Artifact activation crash | Active composition unambiguous after restart |
| TEST-014 | Concurrent tasks | Bound memory/in-flight bytes; correct task correlation |
| TEST-015 | Owner network stop | New work rejected, active work cleaned, local inference preserved |
| TEST-016 | Security profile collusion/abort | Exact profile assumptions and attacks reproduced/reviewed |
| TEST-017 | Learning dropout | Defined abort/threshold; no weakened individual update privacy |
| TEST-018 | DP claim | Accounted budget and composition, not just added noise |
| TEST-019 | Independent peer | Separately written test peer interoperates, not only shared core |
| TEST-020 | NPU unsupported op | Explicit fallback/error with measured placement |
| TEST-021 | Sensitive logging | No prompt/tensor/gradient/key in development/runtime telemetry |

The listed full-product conformance cases remain acceptance targets, not a
blanket passing result. Current executable coverage includes package/workflow
checks, fail-closed scaffold tests and WORK-0010's local diagnostic ledger tests.
The SQLite process-exit test does not satisfy TEST-013 model-file activation.
Use WORK evidence for actual coverage. For numerical tests compare full logits
or operation outputs, not only a sampled string. Performance tests specify
sample size, warm/cold state, units, device/power/network state and uncertainty.
