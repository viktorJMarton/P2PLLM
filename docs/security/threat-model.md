# Threat model — release blocking draft

Assets: prompts, local data, activations/KV cache, gradients/adapter updates, identity keys, model artifacts, availability, task correctness. Adversaries: malicious peer, colluding peers, Sybil identities, relay/observer, malformed model/payload source. A compromised owner OS is outside initial guarantee unless a selected profile explicitly covers it.

## Required distinctions
Confidentiality from network observer; confidentiality from computing peer; inference output leakage; training aggregate leakage; correctness; availability; traffic metadata. State guarantees separately. Transport crypto alone only addresses the first category. Node identity is not proof of personhood or hardware independence.

## Gate
No personal-derived remote work without a local approved profile defining algorithm, implementation revision, corruption/collusion bound, setup/dealer assumptions, allowed outputs/metadata, parameter sizes, adversarial behavior and failure handling. Profile acceptance requires evidence and qualified review. Peer advertisements cannot self-approve profiles.

## Open blockers
Concrete collusion bound and membership enforcement are undecided. A randomly selected set of open peers is not proof of independent parties. Dishonest-majority MPC may provide confidentiality/integrity under stated assumptions but can abort; no guaranteed completion claim. Secure aggregation alone does not protect all information in aggregates and does not solve poisoning. DP requires explicit unit of protection, clipping, accountant, epsilon/delta budget and composition across rounds. MPC/FHE no automatic efficient NPU path.

## Implementation constraints
No arbitrary scripts, pickle models, remote operator graphs outside an allowlist or dynamic native plugins. Bound lengths before allocations; cap decompression/tensor dimensions. Identity keys outside repo/logs. Encrypt transport with established libraries. Use platform-isolated worker where practical; separate thread is not a sandbox. Inference backend no network access by default. Clear buffers best effort; memory-erasure claims need evidence.

Lab profile is synthetic-only and unavailable for public personal-data routing. A user-facing checkbox does not transform unprotected compute into private compute.
