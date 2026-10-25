# Hive feasibility: quantitative research handoff (2026-10-25)

WORK-0003 / run-20261025-hive-math-01. Agent: `math`; primary persona:
Quantitative modeling scientist. Status: research model and proposed measurements,
not an executed distributed experiment or approved privacy profile. Read with
[research handoff](handoff-hive-research-20261025.md) when available. The
[product](../../PRODUCT.md) requires Android and desktop nodes, useful private
cooperative computation **and** learning. The [threat model](../../docs/security/threat-model.md)
and [ADR-003](../../docs/decisions/ADR-003-privacy-gate.md) block personal-derived
remote work until a local profile is reviewed and approved.

## Variables, units and decision rule

For a task, `L` is end-to-end seconds (offer through verified usable result),
`C` compute seconds, `Q` queue seconds, `S` setup seconds, `P` cryptographic
preprocessing seconds, `U,D` transmitted bytes, `R_u,R_d` sustained bytes/s,
`r` interactive network rounds, `RTT` seconds, `V` verification seconds,
`X` expected recovery seconds, `E` owner energy joules, and `M` peak resident
bytes. A conservative serial estimate is

`L_remote = Q+S+P+U/R_u+D/R_d+r*RTT+C_remote+V+X`.

This is an upper-shaped planning decomposition, not a measured identity when
transfers, compute or preprocessing overlap. For pipelined graphs use the
critical path and measure bytes/rounds separately to avoid double counting.
Admit a plan only if its exact operation, output policy, model composition,
memory and **approved** privacy profile match. Compare the same quality and
security contract. For interactive offload claim a benefit only if paired
measured owner CPU **and** complete latency are lower than local with declared
uncertainty intervals excluding parity, as the existing
[experiment plan](experiment-plan.md) requires. Energy claims need energy data.

## Four routes and their mathematical bottlenecks

| Route | Cost/availability model | Privacy and decision boundary |
| --- | --- | --- |
| Independent complete local inference plus P2P offer/scheduling | Per accepted job `L = Q+S+U/R_u+D/R_d+RTT terms+C_peer+V+X`; cold model installation has separate `B_model/R` cost, amortized across a declared finite job count. | Sending a plaintext prompt or recoverable activations to an unknown peer exposes them. Request-level routing is only a synthetic/public-data lab until an approved protective profile covers the operation and output. Encrypted transport alone does not change this. |
| Pipeline or layer partition | For `K` output tokens and `c` sequential inter-peer cuts per token, network-round floor is approximately `K*c*RTT` when cuts cannot overlap for one sequence, plus boundary bytes and queue/compute. More devices increase both cuts and failure exposure. | Petals demonstrates useful large-model resource pooling, but it exposes hidden states and its reported performance is not an Android+desktop/private-Qwen prediction. Keep ordinary layer splitting in a clearly marked synthetic/public-data lab. |
| Bounded protected operation (MPC/FHE) | Include real `P`, party setup, every online message/round, output checks, abort cleanup and both parties' CPU/RSS/traffic. For 2-party protocol, completion requires both parties for the segment; malicious security may safely abort. | WORK-0003's public-`W` exact matrix projection is the first comparable fixture, not full Qwen. MP-SPDZ MASCOT is an experimental candidate. BFV public-`W` has different server-integrity assumptions and needs separate gate. |
| Protected adapter learning | For each round, count local training, protected update traffic, participation window, aggregate verification, evaluation and crash-safe activation. Model utility by paired held-out score, not bytes saved alone. | DiLoCo is a communication baseline, not a privacy mechanism. Secure aggregation, DP and poisoning resistance are distinct gates. For LoRA, `mean(B_i A_i) != mean(B_i) mean(A_i)` generally: scalar pairs `(1,1),(-1,-1)` give mean delta `1` but product of mean factors `0`. Define delta semantics before aggregation. |

The project currently has a 468,633,472-byte old PTE in the published APK and a
2,547,248,816-byte **candidate PTE**, not a 3 GB APK. The candidate's standalone
A72 G01 took 92.172 s and its answer differed from the HF reference; the
published old APK pilot matched 0/7 deterministic fixtures. These observations
are a local quality/resource warning, not evidence for P2P speedup or privacy.
They forbid treating local inference as a finished baseline. The candidate was
not packaged or shipped; see [WORK-0002 checkpoint](../WORK-0002-model-accelerator-baseline/handoff-quality-checkpoint.md).

## Sensitivity calculations (illustrative assumptions, not measurements)

- If `U=1 MiB`, sustained uplink is **assumed** 10 Mbit/s and `r=4`,
  `RTT=50 ms`, upload alone is `8*1,048,576/10,000,000=0.839 s` and round
  floor is `0.200 s`. A remote plan must overcome at least `1.039 s` before
  download, setup, privacy cost, peer compute, queue, checks and recovery. Use
  measured application goodput, including relays and protocol overhead.
- A *hypothetical* 1,024-element, two-byte boundary is 2 KiB. At `K=40` and
  `c=1` with 50 ms RTT, sequential round floor is 2 s. With `c=4`, it is 8 s.
  Real tensors/KV protocol, batching and pipeline concurrency may change this;
  actual Qwen cut shapes and critical path must be measured.
- At an **assumed** 10 Mbit/s, distributing the 2,547,248,816-byte candidate
  PTE once takes at least 2,038 s (34 min) excluding metadata, retries and
  storage. At 100 Mbit/s the bound is 204 s. Preinstalled models avoid this
  per-job cost but still require provenance, version compatibility and a finite
  amortization count. Neither rate is a measured A72 transfer rate.
- If each independent participant survives a segment with probability `p`, an
  all-`k` segment has `p^k` availability. Illustratively `p=.95`: two parties
  `.9025`; three `.8574`; five `.7738`. To obtain `.99` for three required
  participants under independence, each needs at least `.99^(1/3)=.99666`.
  Shared network/power/relay failures invalidate independence, and extra
  identities do not establish non-collusion. A 2-of-3 completion formula
  `3p^2-2p^3=.99275` at `.95` applies only when the selected protocol truly
  tolerates dropout/reconfiguration and its security assumptions survive it.

## Falsifiable experiment sequence

1. Measure local fixed-operation and quality baselines on named A72 and Linux
   desktop hardware: exact model/hash/backend, repeated cold/warm runs, latency,
   owner CPU, memory, energy if instrumented, and English/Hungarian fixtures.
   Do not extrapolate the 92.172 s G01 candidate into token throughput.
2. Measure authenticated connectivity and task transport over same-host,
   two-host LAN, mobile Wi-Fi and mobile-data/NAT topologies. Record direct versus
   relay, connection success, goodput, RTT distribution, setup time, disconnects,
   deadlines and relay limits. libp2p documents NAT traversal and resource-limited
   relays; implementation support is not observed product connectivity.
3. Run the existing [WORK-0003 exact projection plan](experiment-plan.md) with
   pinned real MASCOT preprocessing and its specified synthetic fixtures/faults;
   BFV separately under its own threat assumptions. Record setup-inclusive and
   warm end-to-end costs, bytes, rounds, both parties' CPU/RSS, result checks and
   aborts. The plan's 1 GiB/party, 256 MiB/trial, 120 s trial +5 s cleanup are
   **synthetic lab stop budgets**, not product target promises.
4. Test scheduling using only operations admitted by an approved registry, then
   compare paired local/remote trials under fixed owner and peer resource policy.
   The experiment plan specifies 3 warmups and 30 paired recorded trials per
   shape/variant/topology; report median, p95, failures and uncertainty. Thirty
   trials cannot establish a 99% completion claim: even zero failures require
   at least 299 independent representative trials for a one-sided 95% lower
   confidence bound above 99% (`ln(.05)/ln(.99)`, rounded up). Correlation and
   workload selection still need review.
5. Only after a real protected operation and independent security review, test
   adapter delta semantics, protected aggregation, dropout, poisoning and
   optional DP accounting separately. Held-out utility, owner activation and
   rollback gate learning; DiLoCo's paper performance cannot substitute for a
   phone/desktop or privacy measurement.

## Sources and scope

Primary sources consulted 2026-10-25: [Petals paper](https://arxiv.org/abs/2209.01188),
[DiLoCo paper](https://arxiv.org/abs/2311.08105),
[MP-SPDZ protocol/status documentation](https://mp-spdz.readthedocs.io/en/latest/readme.html),
and [libp2p connectivity guide](https://docs.libp2p.io/guides/standalone-connectivity/).
MP-SPDZ explicitly says its framework has not thereby received the security
review needed for critical production use. No external implementation was
downloaded or run for this mathematical handoff. Proposed formulas and toy
numbers are assumptions; the cited sources do not validate these project
specific performance estimates.
