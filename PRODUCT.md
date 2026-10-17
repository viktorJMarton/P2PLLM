# Product / ecosystem contract
Status: accepted direction; technical feasibility unresolved.

## Intended users
Node operators contributing resources; people using local AI augmented by private peer computation; researchers evaluating distributed inference/learning; independent developers implementing the open protocol.

## Required outcomes
- Run a supported model locally on Android and desktop.
- Discover peers and negotiate operations through authenticated persistent sessions.
- Execute at least one meaningful AI operation privately with unknown peers, not merely transfer encrypted tensors for plaintext execution.
- Complete at least one privacy-preserving cooperative learning round, evaluate the result and allow local activation/rollback.
- Keep personal knowledge and adapters local unless explicitly enrolled under an approved privacy policy.
- Enforce resource limits, cancellation, restart recovery and explicit status.
- Provide documented protocol and independent conformance tests.

## MVP release gates
A supported cooperative AI computation AND learning operation must satisfy a precise security profile, measured utility, target-device feasibility and independent review. A privately computed scalar alone is a primitive milestone, not the whole MVP. Record exact operation/model coverage; do not imply complete private Qwen support from a partial operation.

No default downgrade to plaintext remote execution. A synthetic-data lab is separate, visibly experimental and never accepted as completion of the privacy gate. Original layer-split proposal is a lab baseline, superseded as a public MVP architecture until protected execution exists.

## Android operator experience
Screens: overview; AI session; network jobs; models/learning; resources/privacy. Roles are independently toggled: personal inference, contribution, learning. A master network stop rejects new jobs and terminates/cleans active network work. Local inference may continue. UI displays actual mode and unavailable capability, never unproven confidentiality claims.

## Desktop experience
CLI for lifecycle, status, models, resource policies, jobs, learning and structured event export. Initial reference platform Linux x86_64; Android arm64-v8a. Other platforms are later targets, not verified support.

## First release exclusions
Arbitrary remote code, mandatory crypto token economy, anonymous-network guarantees, guaranteed global availability, unrestricted full-model retraining on all phones, all-model/all-NPU compatibility, closed-group implementation. No camera permission is needed merely to use an NPU.

## Core acceptance IDs
REQ-001 local inference; REQ-002 authenticated session; REQ-003 private shared compute; REQ-004 private shared learning; REQ-005 resources/cancellation; REQ-006 restart consistency; REQ-007 interoperability; REQ-008 update provenance/rollback; REQ-009 traceable development; REQ-010 accelerator profiling.
