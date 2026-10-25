# P2PLLM — 100-aspect review and change backlog

**Status:** review proposals, **not** 100 completed implementation cycles, audits, tests, experiments or validated security findings.  
**Reviewed baseline:** `PRODUCT.md` from `docs/product-contract-expansion`, plus `TECHNOLOGY.md`, `AGENTS.md`, `BUILD.md`, `GOVERNANCE.md`, `docs/security/threat-model.md`, `docs/architecture/overview.md`, `docs/decisions/INDEX.md`, `tests/conformance-matrix.md`, `work/INDEX.md`, eight WORK briefs and selected ADRs.  
**Method:** 10 different domains × 10 independent review lenses = 100 individually actionable units. Each item records a proposed clarification/test/change, not a claim the implementation is defective. Root entry points and privacy gates remain authoritative.

## Triage rules

- **P0:** directly blocks truthful release, personal-data privacy, key security or control-plane safety.
- **P1:** required for reproducible MVP acceptance and interoperability.
- **P2:** usability, governance or future robustness that can be scoped after foundations.
- An item is complete only when linked to a WORK owner, accepted change, test/evidence, and (where security-sensitive) qualified independent review.
- Current repository evidence is documentary; no empirical testing is claimed by this review.
- Proposed additions must not override accepted ADRs without a new recorded decision.

## 1. Product positioning

Evidence entry: PRODUCT.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-001 | P1 | Distinguish protocol interoperability from product UI completeness; add separate release evidence. |
| AUD-002 | P1 | Specify the minimum useful local assistant scenario and reference prompt suite. |
| AUD-003 | P1 | Define 'meaningful AI operation' with task-level quality acceptance, not scalar arithmetic. |
| AUD-004 | P1 | Separate user-facing privacy promises from technical backend capability flags. |
| AUD-005 | P1 | State the minimum viable number of distinct nodes and roles for a demo. |
| AUD-006 | P1 | Specify degraded offline behavior when discovery or peers are unavailable. |
| AUD-007 | P1 | Define how first-run model acquisition behaves without an account. |
| AUD-008 | P1 | Require accessibility and localization decisions before public UX release. |
| AUD-009 | P1 | Separate open-source code availability from model-weight redistributability. |
| AUD-010 | P1 | Add explicit non-goals for financial incentives and network monetization. |

## 2. Identity and trust

Evidence entry: docs/security/threat-model.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-011 | P1 | Specify identity creation and key storage on Android and Linux. |
| AUD-012 | P1 | Define key rotation without breaking persisted jobs and reputation links. |
| AUD-013 | P1 | Define lost-key recovery and its effect on peer trust. |
| AUD-014 | P1 | Distinguish node pseudonymity from anonymity in UI copy. |
| AUD-015 | P1 | Document Sybil attack limitations for open peer membership. |
| AUD-016 | P1 | Define peer revocation and cached credential expiration semantics. |
| AUD-017 | P1 | Make bootstrap trust roots explicit and test compromise response. |
| AUD-018 | P1 | Specify how clock skew affects credentials, leases and replay windows. |
| AUD-019 | P1 | Reject self-attested security-profile approvals in all protocol paths. |
| AUD-020 | P1 | Add negative tests for identity collision and impersonation attempts. |

## 3. Discovery and routing

Evidence entry: ADR-004-open-groups.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-021 | P1 | Specify at least one concrete bootstrap/discovery method and operational ownership. |
| AUD-022 | P1 | Define NAT traversal fallback and no-connectivity error state. |
| AUD-023 | P1 | Limit discovery advertisements to metadata necessary for routing. |
| AUD-024 | P1 | Define TTL and staleness behavior for capability/skill advertisements. |
| AUD-025 | P1 | Separate measured capability from self-reported expertise and reputation. |
| AUD-026 | P1 | Model malicious ratings, collusion and reputation farming before ranking peers. |
| AUD-027 | P1 | Specify selection diversity without equating independent IDs with independent parties. |
| AUD-028 | P1 | Define routing behavior when only ineligible privacy profiles are available. |
| AUD-029 | P1 | Bound fanout, retry storms and background network discovery energy. |
| AUD-030 | P1 | Define compatibility of future closed-group membership with v1 message schema. |

## 4. Protocol and interoperability

Evidence entry: tests/conformance-matrix.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-031 | P0 | Pin a wire schema compatibility policy across minor and major releases. |
| AUD-032 | P0 | Specify unknown-field handling and canonical serialization where signed. |
| AUD-033 | P0 | Define idempotency key scope across reconnection and process restart. |
| AUD-034 | P0 | Set explicit frame, tensor, compression and nesting limits before allocation. |
| AUD-035 | P0 | Specify stream ordering, deduplication and out-of-order error handling. |
| AUD-036 | P0 | Document session negotiation downgrade resistance. |
| AUD-037 | P0 | Define retransmission, deadlines and cancellation acknowledgment semantics. |
| AUD-038 | P0 | Test malformed payloads with an independently implemented peer. |
| AUD-039 | P0 | Prove integrity checks and computation-correctness proofs are distinct. |
| AUD-040 | P0 | Publish versioned golden vectors and machine-readable error codes. |

## 5. Private computation

Evidence entry: WORK-0003, WORK-0005.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-041 | P0 | Select the smallest AI-useful protected subgraph and formalize its semantics. |
| AUD-042 | P0 | Enumerate values revealed to each compute party and relay. |
| AUD-043 | P0 | Document honest-majority versus dishonest-majority assumptions. |
| AUD-044 | P0 | Quantify collusion thresholds under real open-peer selection limits. |
| AUD-045 | P0 | Model setup/dealer requirements and compromised setup risk. |
| AUD-046 | P0 | Define passive/active attacker capabilities and abort guarantees. |
| AUD-047 | P0 | Measure arithmetic accuracy against the pinned plaintext reference. |
| AUD-048 | P0 | Measure bytes, interaction rounds, memory and energy on target devices. |
| AUD-049 | P0 | Prohibit plaintext fallback when private backend unavailable or too slow. |
| AUD-050 | P0 | Require independent cryptographic review bound to exact implementation revision. |

## 6. Learning, quality and updates

Evidence entry: WORK-0006.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-051 | P0 | Specify initial adapter format and immutable base/tokenizer compatibility. |
| AUD-052 | P0 | Define eligible local training data and explicit enrollment policy. |
| AUD-053 | P0 | Separate secure aggregation confidentiality from output leakage. |
| AUD-054 | P0 | State participation threshold and dropout recovery without exposing updates. |
| AUD-055 | P0 | Threat-model poisoning, backdoors and adversarial adapter updates. |
| AUD-056 | P0 | Define DP protection unit and epsilon/delta accounting if DP claimed. |
| AUD-057 | P0 | Specify held-out datasets and measurable utility beyond one training loss. |
| AUD-058 | P0 | Define deterministic round IDs, replay defense and duplicate update behavior. |
| AUD-059 | P0 | Ensure atomic adapter activation with filesystem/database crash tests. |
| AUD-060 | P0 | Require signed provenance, local user approval and reliable rollback. |

## 7. Model and accelerator support

Evidence entry: TECHNOLOGY.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-061 | P1 | Pin exact Qwen model/tokenizer revisions and verify model licenses. |
| AUD-062 | P1 | Measure 0.6B diagnostic versus 1.7B useful candidate on actual devices. |
| AUD-063 | P1 | Report quantization loss with logit-level and task-level comparisons. |
| AUD-064 | P1 | List unsupported ExecuTorch operators and their CPU fallback paths. |
| AUD-065 | P1 | Measure cold start and sustained thermal throttling separately. |
| AUD-066 | P1 | Measure RAM peaks, KV-cache growth and OOM behavior under contention. |
| AUD-067 | P1 | Inventory actual GPU/NPU/DSP backend availability rather than SoC branding. |
| AUD-068 | P1 | Document vendor binary redistribution and deployment restrictions. |
| AUD-069 | P1 | Compare data-transfer overhead against accelerator compute gain. |
| AUD-070 | P1 | Never infer NPU support or request camera permission from ISP presence. |

## 8. Android and desktop UX

Evidence entry: WORK-0007, BUILD.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-071 | P2 | Test all three roles independently and in every two-role combination. |
| AUD-072 | P2 | Define master stop semantics while local inference remains live. |
| AUD-073 | P2 | Surface actual privacy mode per job; avoid blanket encrypted-equals-private labels. |
| AUD-074 | P2 | Render blocked capability and missing backend with actionable explanation. |
| AUD-075 | P2 | Implement foreground/background lifecycle constraints per Android versions. |
| AUD-076 | P2 | Validate charging/Wi-Fi/battery-floor changes during an active contribution. |
| AUD-077 | P2 | Show detailed job budget use and cancellation cleanup status. |
| AUD-078 | P2 | Specify secure identity backup/import UX and destructive confirmation. |
| AUD-079 | P2 | Require CLI JSON event parity with Android job state transitions. |
| AUD-080 | P2 | Verify accessibility, keyboard navigation and screen reader status announcements. |

## 9. Resilience and operations

Evidence entry: docs/architecture/overview.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-081 | P1 | Formalize lifecycle/network/task/update state machines and illegal transitions. |
| AUD-082 | P1 | Define a durable job lease and expiration protocol across reboots. |
| AUD-083 | P1 | Verify idempotent execution avoids duplicated private steps/KV updates. |
| AUD-084 | P1 | Test cancellation races against completion and model activation. |
| AUD-085 | P1 | Specify buffer cleanup limits without claiming perfect memory erasure. |
| AUD-086 | P1 | Apply per-peer and global RAM/bandwidth/concurrency admission limits. |
| AUD-087 | P1 | Bound retry backoff and prevent storms after network restoration. |
| AUD-088 | P1 | Define operator pause versus shutdown versus emergency master stop. |
| AUD-089 | P1 | Ensure telemetry redaction on errors, panics and diagnostic exports. |
| AUD-090 | P1 | Test SQLite migration and interrupted filesystem-plus-DB transactions. |

## 10. Governance, delivery and traceability

Evidence entry: AGENTS.md, GOVERNANCE.md, work/INDEX.md.

| Review ID | Priority | Review / requested action |
|---|---|---|
| AUD-091 | P2 | Map REQ-011–017 to work briefs and test cases; current queue lists mostly REQ-001–010. |
| AUD-092 | P2 | Assign an evidence owner and independent reviewer per release gate. |
| AUD-093 | P2 | Prevent review-only changes from being reported as implemented behavior. |
| AUD-094 | P2 | Add a release checklist differentiating synthetic lab, preview and public MVP. |
| AUD-095 | P2 | Define code license via owner decision; do not silently grant one. |
| AUD-096 | P2 | Inventory third-party model, SDK, library and training-data licenses. |
| AUD-097 | P2 | Publish security disclosure, maintenance and dependency update policy. |
| AUD-098 | P2 | Require immutable build artifacts, SBOM and reproducible version manifests. |
| AUD-099 | P2 | Capture Android APK artifact naming plus release/debug notes per minor version. |
| AUD-100 | P2 | Define a stop/go decision record when either private compute or learning gate fails. |

## Concrete repository changes proposed

1. Add `docs/reviews/100-aspect-audit.md` as an auditable review backlog (this file).
2. Extend `docs/traceability.md` with REQ-011–017 work and test mappings once owners and test IDs are agreed; do not mark new tests passing.
3. Add a release-gate evidence template per private operation: algorithm/version, security assumptions, attack surface, target device, utility, performance, review and signed approval.
4. Add protocol conformance cases for identity rotation, stale discovery, invalid negotiation, cancellation races and independent implementation.
5. Create separate measured mobile benchmark reports and learning privacy-accounting reports rather than embedding unsupported claims in PRODUCT.md.

## Recommended review waves

| Wave | Review IDs | Output |
|---|---|---|
| A — Security and release truth | AUD-011–020, AUD-031–060 | Threat-profile, private compute and protected learning design decisions |
| B — Interoperability and reliable operations | AUD-021–030, AUD-081–090 | Protocol changes, conformance vectors and recovery scenarios |
| C — Device proof and UX | AUD-061–080 | Reference-device measurements, operator lifecycle and status UX |
| D — Product and governance | AUD-001–010, AUD-091–100 | Measurable scope, traceability, ownership, release record |

## Completion record template

For each `AUD-NNN`: linked `REQ` / `WORK`; current evidence and commit; finding classification (verified gap / design proposal / unknown); decision and rationale; changed paths; tests and exact result; reviewer; residual risk; state (`open`, `accepted`, `rejected`, `implemented`, `verified`).

**Do not bulk-mark items verified.** This is a review backlog to drive successive evidence-based engineering work, and no private computation or learning gate is approved by its creation.
