# Product / ecosystem contract

Status: **accepted product direction; technical feasibility unresolved**. This is a normative product target, not evidence that the system exists or that private Qwen inference/training has been demonstrated. The repository is an **open-source ecosystem and interoperable protocol**, not a centrally operated AI SaaS or a token product.

## Vision and problem

P2PLLM lets a person run a useful AI assistant on their own device while optionally borrowing constrained computation from a distributed set of independently operated peers. It also investigates privacy-preserving cooperative improvement of model adapters. Participants retain control over local data, models, compute budgets, roles and accepted updates.

A mobile phone should be a first-class node, not just a remote-control client. The network must be useful without assuming every phone can host a full model, every device has an accessible NPU, or every peer is trustworthy. A local-only experience remains available when peers, private backends or connectivity are absent.

**Product promise is conditional:** a remote operation may be called private only for an explicitly approved operation, threat model, protocol implementation and tested deployment profile. Encryption of packets alone does not make remote computation confidential.

## Intended users

- **Personal AI users:** run local inference, selectively request protected network help and keep personal context local by default.
- **Node operators:** donate opted-in spare compute under explicit battery, thermal, network, storage and time limits.
- **Learning participants:** explicitly enroll eligible updates in a reviewed privacy-preserving learning round and approve resulting adapters locally.
- **Researchers:** reproduce benchmarks, security assumptions, failure experiments and learning utility.
- **Independent developers:** implement the open, versioned protocol and run conformance tests without relying on one privileged client or coordinator.

## Guiding product principles

1. Local-first, offline-capable personal inference; opt-in network involvement.
2. Open protocol and reference implementations; independent peers can interoperate.
3. Fail closed for protected operations; never silently downgrade to plaintext execution.
4. Data minimization, consent, least privilege and evidence-backed privacy claims.
5. Measurable utility and feasibility over speculative hardware or cryptography claims.
6. Transparent, cancellable resource contribution and crash/restart consistency.
7. Reproducible, versioned model artifacts, training rounds and development decisions.
8. Explicit separation of public release, experimental labs and future research.

## Required outcomes

- Run a pinned, supported model locally on Android arm64-v8a and Linux x86_64 desktop.
- Discover peers, authenticate identities and negotiate explicitly supported operations over persistent encrypted sessions.
- Execute at least one **meaningful AI operation** cooperatively and confidentially against unknown peers under an approved security profile; encrypted tensor transfer followed by plaintext peer execution does not qualify.
- Complete at least one privacy-preserving cooperative adapter-learning round, evaluate utility/security and permit explicit local activation or rollback.
- Keep prompts, personal knowledge, retrieval indexes, conversations, raw documents and private adapters on device unless the user expressly enrolls a defined artifact under an approved data policy.
- Support per-role resource limits, fair scheduling, cancellation, master network stop, idempotent job recovery and truthful observable status.
- Provide an open versioned protocol, an independently implemented test peer, conformance vectors, negative tests and reproducible evidence.
- Profile CPU/GPU/NPU/DSP capability and fallback on actual reference devices; do not infer support from advertised silicon.

## Product modes and roles

Roles are independent toggles, not mutually exclusive account types:

| Role | Purpose | Default data boundary |
|---|---|---|
| Personal inference | Local interactive assistant, optional protected remote subtask | Prompts and personal context stay local unless an approved operation specifically authorizes disclosure of defined inputs |
| Contribution | Execute allowlisted, bounded network operations | No access to the operator's unrelated local knowledge or app data |
| Learning | Join explicitly enrolled, approved adapter learning rounds | Only policy-approved updates/protocol messages leave the device |

The network-wide master stop blocks admission, cancels or drains active network jobs according to policy, cleans transient state and disables contribution/learning/network-assisted inference. **Local inference may continue.** UI and CLI must distinguish enabled, connected, negotiating, executing, cancelled, failed, unavailable and locally-only states.

No role switch silently grants access to personal data, background compute, mobile data or a new privacy policy. Consent is specific and revocable for future work; already disclosed information cannot be retroactively recalled.

## User journeys

1. **Offline first run:** install app/CLI, see device capability, obtain a pinned model from a verified source, run a local prompt without an account or peer.
2. **Join open network:** create/import node identity, discover peers, authenticate, advertise only opted-in capabilities, inspect peer/protocol compatibility and connection health.
3. **Request network assistance:** user selects an approved private operation, sees availability, expected data exposure, resource/cost envelope and fallback; receives a result or an explicit privacy-safe failure.
4. **Contribute resources:** operator configures CPU threads, RAM, disk, battery floor, charging/Wi-Fi requirements, thermal thresholds, bandwidth, concurrency and daily budgets; can pause/stop immediately.
5. **Cooperative learning:** opt in to a specific round, model/adapter version, data category, security and disclosure policy; validate the result, compare against baseline and activate or roll back locally.
6. **Recover:** after app kill, reboot or disconnect, reconcile persisted jobs, leases, identities and model state; do not duplicate execution or claim unverified completion.

## Model and local AI scope

- Initial model family: **Qwen**, with Qwen3-0.6B a diagnostic baseline and Qwen3-1.7B a candidate for useful mobile inference. Neither model/device combination is deemed supported until pinned and measured.
- PyTorch/Hugging Face/PEFT are research and adapter-training tools; ExecuTorch is the targeted Android inference path, with Rust shared node core and Kotlin/Jetpack Compose UI. A llama.cpp comparison may be used for benchmarking, not as an unannounced runtime substitution.
- Publish a support matrix keyed by exact model revision, tokenizer, quantization, execution backend, ABI, device, memory, latency, correctness, thermal/battery behavior and license. A pass for one operation or one phone does not establish full-model support.
- Local personal knowledge can be indexed/retrieved for local inference. Network workers must not receive whole conversations, raw documents, embeddings or adapters by default; embeddings and gradients can themselves leak information.
- Base model and adapters are separately versioned. Activation is atomic, user-approved and reversible, with compatibility and signature/hash checks.

## Peer network and protocol

- Open-peer discovery first. Closed groups and curated expertise communities are future protocol-compatible extensions, **not** first-release implementations.
- Identity is based on authenticated cryptographic keys; node identity is not proof of a unique human or independent device. Specify trust-on-first-use/rotation/revocation behavior before accepting real-world traffic.
- Maintain persistent authenticated sessions where possible; negotiate protocol version, operation ID, supported security profile, algorithm revision, model compatibility, maximum payload, resource caps, deadline and cancellation semantics.
- Candidate implementation: rust-libp2p with QUIC and investigated fallbacks. Exact transport compatibility is a measured decision, not guaranteed.
- Every job and packet carries collision-resistant identifiers, correlation, sequence/replay protection, bounded lifetime and authenticated integrity. Use established encryption, not custom cryptography; blockchain/NFT is not required.
- Support signed/validated peer advertisements and coarse **self-reported expertise/capability indexes** (e.g. model operations, accelerators, benchmarks). Reputation or ratings may inform routing only after manipulation/Sybil risks are documented; they are not security proofs.
- Partition work only along supported, explicitly defined operation boundaries. A single transport session can multiplex jobs, but is not permission to send arbitrary executable tasks.
- Publish message schema, version negotiation, error codes, canonical vectors, test fixtures and independent implementations. Unknown operation/version/profile must fail clearly.
- No arbitrary remote code, dynamic peer-supplied native plugins, untrusted pickle models or unconstrained operator graphs.

## Private cooperative computation — non-negotiable gate

The original layer-split model where peers see intermediate activations is retained **only as a synthetic-data lab baseline**; it is superseded for public personal-data routing until confidentiality is demonstrated. TLS, packet encryption and obfuscation do not protect data from the peer performing plaintext arithmetic.

Select and document an auditable protected-computation approach for an **AI-relevant** operator or subgraph (e.g. reviewed MPC/FHE/hybrid design). MP-SPDZ and OpenFHE are research candidates, not preselected production guarantees. Record exactly:

- Supported model/operator graph, tensor shape/precision and threat profile.
- What each peer sees: inputs, shares, intermediate values, outputs, lengths, timing and metadata.
- Corruption/collusion threshold, party selection/independence assumptions, setup/trusted dealer assumptions, active versus passive adversary and abort behavior.
- Correctness/error bounds, leakage analysis, replay resistance, protocol failure handling and limits on repeated queries.
- Communication bytes, rounds, latency, RAM/CPU/energy and comparison with local-only execution on reference hardware.
- Review evidence, cross-implementation tests and public reproducibility instructions.

If protection is infeasible on target devices, mark the gate blocked and keep network assistance disabled for personal data. A privately computed scalar is a primitive milestone, **not an MVP**. Do not imply end-to-end private Qwen support from a partial operator.

## Cooperative learning — separate non-negotiable gate

Initial learning target is a **bounded adapter update** (e.g. LoRA/PEFT-compatible), not unrestricted global base-model retraining. A learning round must:

1. Pin baseline model, adapter architecture, dataset eligibility and update format.
2. Require explicit enrollment, with a clear distinction between synthetic experiments and personal-data rounds.
3. Bound local computation and perform local update validation/clipping as specified.
4. Protect individual updates under a reviewed aggregation protocol; evaluate dropout, malicious contributions, poisoning and reconstruction risk.
5. Specify whether differential privacy is needed and, if so, the unit of protection, clipping, noise mechanism, ε/δ, accountant and cumulative budget.
6. Produce a versioned candidate with provenance, aggregate metrics and a validation report.
7. Evaluate held-out utility against the baseline and rollback candidate; require local opt-in activation.
8. Recover deterministically from interrupted rounds without reusing unsafe randomness or counting privacy budgets incorrectly.

Secure aggregation alone does not make a released aggregate harmless and does not eliminate poisoning. Peer scoring and aggregated learning quality are separate from confidentiality.

## Android operator experience

Required screens:

| Screen | User-visible responsibilities |
|---|---|
| Overview | Node state, active roles, local/network mode, health, pending jobs and master stop |
| AI session | Local chat, supported model/mode, network request eligibility, progress, error and cancellation |
| Network jobs | Incoming/outgoing jobs, state transitions, deadlines, peer/session identifiers, resource consumption and retry reason |
| Models & learning | Installed models/adapters, exact versions, capability, learning round consent, evaluation, activation and rollback |
| Resources & privacy | CPU/RAM/storage/battery/thermal/bandwidth policies, Wi-Fi/charging-only switches, disclosure/security profile and identity management |

Additional requirements: accessible status and actions, notification/background-execution rules consistent with Android platform restrictions, permission minimization, honest offline/unsupported states, and no battery or network contribution without opt-in. The app need not request camera access just to discover or use an NPU. Camera ISP is not assumed to be a general compute device.

## Desktop reference experience

Linux x86_64 CLI initially; matching node-core behaviors and protocol. Commands should cover node lifecycle, identity, peer/session inspection, supported models, local prompts, roles, resource policies, job submit/cancel/status, learning enrollment/evaluation/activation/rollback, health and structured event export. Structured output must be machine-readable with stable error codes for automation and conformance tests. Other desktop operating systems are later targets, not currently verified.

## Scheduling, operations and resilience

- Admission control before accepting work; per-peer and global caps for CPU, memory, disk, bandwidth, concurrency, time, battery and thermal pressure.
- Priority policy keeps personal/local interaction responsive; background contribution yields under contention.
- Deadlines, bounded queues, backpressure, cancellation propagation, timeout and retry limits; reject work safely when exhausted.
- Persist minimal recoverable job state in node-owned SQLite with schema migrations, idempotency keys and well-defined restart reconciliation.
- Distinguish cancellation requested, worker stopped and transient data cleaned; never display success merely because a request was sent.
- Telemetry is opt-in/minimized, redact secrets and personal payloads, export structured events with correlation IDs and reproducible diagnostics.
- No guarantee of peer uptime or global network availability; disclose degraded/local-only operation.

## Security, governance and supply chain

- Maintain a threat model for malicious/colluding/Sybil peers, observers, compromised model supply, malformed payloads, poisoning, denial of service and metadata leakage.
- Define approved security-profile registry and release approval authority; peer-advertised profiles do not self-certify.
- Verify model artifacts, dependencies, binaries and adapter updates against pinned hashes/signatures/provenance. Keep identity keys outside repository and logs.
- Explicit privacy policy for each remotely disclosed category. Data retention, deletion, log redaction and consent state must be documented and tested.
- Version wire schema; define backward compatibility, protocol negotiation, deprecation and capability probing. Publish open-source license and contribution/security-disclosure policy before public release; current license is unresolved.
- Development work is traceable through work IDs, acceptance evidence, code review, test reports and architecture decisions. Automated agents may draft/implement/review but cannot declare security gate passed without independent qualified review.
- Reproducible build, SBOM/dependency licenses, pinned toolchains and artifact provenance are release inputs. Minor-version APK packaging with debug/release notes is a desired workflow, not evidence that artifacts already exist.

## Platform and technology decisions

The canonical technology choices, statuses and version policy are in [TECHNOLOGY.md](TECHNOLOGY.md). Architecture decisions are in [docs/decisions/INDEX.md](docs/decisions/INDEX.md); detailed threats in [docs/security/threat-model.md](docs/security/threat-model.md). Product requirements here do **not** assert that chosen frameworks, accelerators or private-compute candidates have been installed, integrated or audited.

## MVP release gates

**Release requires both useful protected cooperative AI computation and protected cooperative learning**, plus independently repeatable evidence:

| Gate | Minimum evidence |
|---|---|
| Local | Pinned model executes correctly on at least one specified Android arm64-v8a and Linux x86_64 reference device with measured feasibility |
| Sessions | Independent peer can discover/authenticate/negotiate, reject incompatible messages and recover from reconnect/replay |
| Private compute | Useful reviewed AI operator/subgraph with explicit leakage/collusion profile, utility and target-device performance |
| Private learning | Completed secure adapter round with evaluation, attack/dropout tests, bounded privacy accounting where applicable and local rollback |
| Operations | Enforced budgets, stop/cancel, bounded resource use, restart tests and accurate UI/CLI state |
| Interoperability | Open protocol spec, cross-implementation vectors and independently built conformance peer |
| Delivery | Reproducible builds, provenance/security review, licensing, documentation and traceable acceptance evidence |

A synthetic-data lab must be marked **EXPERIMENTAL** and never counts as passing a privacy gate. There is no default plaintext remote fallback. Failure of either private-compute or private-learning gate blocks the public MVP claim, though useful local-only or research previews may be labeled separately.

## Milestone progression

1. **M0 — Reproducible foundation:** repository, pinned toolchains, CI, Rust core, Kotlin/UniFFI and Linux CLI smoke tests, Android debug build.
2. **M1 — Local intelligence:** pinned Qwen diagnostic and candidate models, correctness, quantization and accelerator benchmark matrix.
3. **M2 — Trustworthy transport:** identity, authenticated sessions, protocol schemas, independent peer, negative tests and resource lifecycle.
4. **M3 — Privacy primitive lab:** synthetic-only MPC/FHE/aggregation candidates, concrete threat and collusion profile, measured cost; no product privacy claims.
5. **M4 — Useful private inference:** approved operation integrated with scheduler and client, security review, correctness/latency tests.
6. **M5 — Protected adapter learning:** enrolled privacy-preserving round, measurable improvement, provenance and atomic activation/rollback.
7. **M6 — Android UX and release integration:** roles, master stop, offline continuity, packaging, conformance, documentation and independent release gate decision.

The executable queue in [work/INDEX.md](work/INDEX.md) is authoritative for immediate implementation order. Milestone names above are outcomes, not claims that work is complete.

## First-release exclusions

- Arbitrary remote execution, unreviewed plugins or unrestricted peer-provided computation.
- Mandatory cryptocurrency, blockchain/NFT identity or token economy.
- Anonymous-network guarantees, Sybil-proof identity, guaranteed global availability or secure routing merely from ratings.
- Unrestricted full-model training on all phones, every model format, every NPU/GPU, or camera/ISP compute.
- Closed/private group implementation, federated personal knowledge synchronization and a general marketplace.
- Unqualified claims of private full-Qwen inference, zero-knowledge guarantees, secure enclaves, zero-copy acceleration or independent peers.
- Public personal-data computation using the original plaintext layer split.

## Requirement and acceptance register

| ID | Acceptance target |
|---|---|
| REQ-001 | Version-pinned local model inference on named Android and Linux references with performance evidence |
| REQ-002 | Authenticated persistent peer session, version/capability negotiation and negative tests |
| REQ-003 | Useful private shared AI computation with approved threat profile and independent review |
| REQ-004 | Privacy-preserving shared adapter round, utility measurement and approved local activation |
| REQ-005 | Enforced resources, cancellation, stop semantics and truthful state |
| REQ-006 | Restart/reconnect consistency, bounded retry and durable job reconciliation |
| REQ-007 | Public protocol and independent conformance suite/test peer |
| REQ-008 | Signed/pinned update provenance, compatibility validation and rollback |
| REQ-009 | Traceable development, reproducible tests, evidence and review |
| REQ-010 | Actual hardware capability and accelerator/CPU fallback profiling |
| REQ-011 | Per-role opt-in, consent, disclosure boundary and network master stop |
| REQ-012 | Personal knowledge and adapter locality with explicit policy-controlled exceptions |
| REQ-013 | Peer expertise advertisement/routing with documented untrusted-reputation limits |
| REQ-014 | Android/CLI state parity and machine-readable diagnostics |
| REQ-015 | Model/backend/device support matrix and exact operator coverage |
| REQ-016 | Learning provenance, poisoning/dropout evaluation and privacy budget handling |
| REQ-017 | Supply-chain verification, open-source licensing and release documentation |

REQ-011–017 are product refinements proposed here; work-item mappings and concrete test cases must be added to the traceability matrix before they can be marked satisfied.

## Open decisions and proof obligations

- Select a concrete private-compute algorithm, implementation and acceptable collusion profile for an AI-useful operation; quantify peer independence assumptions.
- Prove feasibility on target Android and Linux hardware, including networking overhead and availability when the phone is under thermal/battery pressure.
- Select the learning privacy/aggregation design, dropout threshold, poisoning defenses and explicit DP accounting policy.
- Finalize supported Qwen revisions, tokenizer/quantization/export path and license checks.
- Specify discovery/routing topology, bootstrap independence, NAT traversal and identity recovery without promising anonymity.
- Decide first-release measurement thresholds (quality, latency, memory, power, security review checklist) **from observed benchmarks**, not invented numbers.
- Decide governance, contributor license, user-data consent wording, permissible telemetry and independent review process.
- Define whether any compensation/incentive mechanism is warranted after a useful non-token protocol exists.

**Decision discipline:** Product aspiration, design acceptance, demonstrated capability and reviewed release approval are four distinct states. Never label one as another.
