# Synthetic private linear-operation experiment plan

Status: proposed preparation only, 2026-10-22. No experiment executed.
WORK-0003 / run-20261022-privacy-plan-01. REQ-003; REQ-004 is not tested by
this inference primitive. Role: security; persona: Constructive adversarial
security reviewer. Source baseline: ba6b116f15567ba0469040ff1b73542e57d7f71c,
branch work/WORK-0002-phone-baseline; plan is uncommitted.

The current sprint prioritizes WORK-0002 local-model/device measurements. This
document prepares a separate research experiment without changing the approved
[registry](../../docs/security/privacy-profile-registry.md), whose approved
profiles remain **none**. Personal-derived remote work remains unavailable.
Requirements remain [PRODUCT](../../PRODUCT.md), [threat model](../../docs/security/threat-model.md),
[ADR-003](../../docs/decisions/ADR-003-privacy-gate.md) and
[RFC-0002](../../docs/rfcs/RFC-0002-compute.md).

## Operation and numerical contract

Test a matrix projection `Y = X W`, one building block of a transformer FFN,
using independently generated synthetic matrices only. Start with shapes
`X[1,64] W[64,128]`, then `X[1,256] W[256,512]`. These are reduced fixtures,
not asserted Qwen layer dimensions. Mapping to a real pinned Qwen configuration,
nonlinear activation, gates, residuals, attention/KV state and full token
generation are separate later work. A successful small projection is a
primitive milestone, not meaningful complete cooperative AI or MVP acceptance.

Use signed integer inputs `Xq,Wq in [-127,127]`; interpret real inputs as
`Xq/128,Wq/128`. Compute the integer accumulator exactly and dequantize only at
the owner as `Yq/16384`. No secure truncation or probabilistic rounding occurs
in this first workload. For each output, `abs(Yq) <= D * 16129`; at D=256 this
is 4,129,024. The selected prime/signed decoding must represent twice that
bound without wraparound. This bound is a workload calculation, not measured
model quality. Any future rescaling or approximation changes this contract.

Fixture suite: zero, positive/negative extremes, alternating signs,
single-nonzero rows/columns and 30 deterministic synthetic fixture seeds with
the generator algorithm/version pinned before execution. Compare every output
to a separately implemented wide-integer oracle, element for element. Persist
only shape, fixture ID, bounded aggregate error and pass/fail; no tensors,
shares, model activations, keys or raw input/output files in evidence bundles.
Seeds identify disposable synthetic fixtures only, never cryptographic RNG.

Primary variant **public-W**: immutable public synthetic weights are bound into
the allowlisted program and manifest; X is private to owner P0. This resembles
open model weights, but its linear arithmetic may be cheaper locally than any
offload. Measure that possibility rather than claiming acceleration.

Separate optional variant **secret-W**: P1 inputs W, P0 inputs X; reveal Y only
to P0. This exercises secret multiplications but changes the functionality and
disclosure model. It is not an equivalent performance comparison to public-W,
and does not authenticate P1's chosen weights as a specified Qwen model.
An adversary changing its allowed input is not itself a protocol integrity
failure. Private-W ranges need secure range checking with a declared validity
bit/abort leak and measured cost before bounded signed-real semantics apply;
otherwise label the result finite-field-only and fail the signed-real gate.

## Candidate, comparator and assumptions

First candidate: MP-SPDZ **MASCOT**, two-party malicious/dishonest-majority
arithmetic over a prime field. Its protocol paper supports this research choice;
the framework also documents SPDZ2k as a malicious ring alternative. Choosing
MASCOT avoids introducing ring truncation in the initial exact accumulator.
This is an experiment recommendation, not backend adoption or an audit finding.
See [MASCOT paper](https://eprint.iacr.org/2016/505),
[SPDZ2k paper, revised 2022](https://eprint.iacr.org/2018/482) and
[MP-SPDZ protocol matrix](https://mp-spdz.readthedocs.io/en/latest/readme.html#protocols).

P0 is the data owner and a computing party; P1 is an unknown contributing peer.
Evaluate one statically corrupted party, with the other party honest. For owner
input confidentiality P0 and its OS/key storage are trusted; P1 may be corrupt
and coordinate with observers or other peers outside this two-party session.
There is no third honest server, honest-majority election, or assumption that
two remote identities represent independent owners. If the owner is corrupted,
its own input is already disclosed; corruption of both parties is outside the
confidentiality claim. Adaptive corruption and cross-session composition are
unproved until separately reviewed.

Required setup: independently generated cryptographic randomness, authenticated
party identities/channels, matching program/parameter digests, full real OT-based
preprocessing, and fresh single-use preprocessing material. No trusted dealer
is assumed. Fixture certificates are provisioned only for isolated host trials;
the actual authentication/configuration path needs inspection. No default
privacy parameter is accepted merely because a binary runs. Propose 128-bit
computational target and separately recorded statistical-check parameters for
review; concrete prime, OT, MAC, repetition/composition bounds and their exact
implementation mapping remain **unresolved execution blockers**, not a claim of
a universal failure probability. No DP mechanism or epsilon is defined here.

Output policy: only P0 obtains designated Y after the backend's required
integrity checks. P1 learns public dimensions, variant/program/parameter digests,
party addresses, message sizes/timing and completion/abort. Disclose additional
range-validity leakage only if that variant enables a reviewed check. No public
intermediate openings, public Y, plaintext fallback or output-before-check
acceptance. P0 learns Y and therefore whatever follows from its chosen X and Y;
secret-W is not a promise against model extraction. Abort/fairness and guaranteed
availability are not promised. Repeated chosen-input sessions require separate
output/composition review.

Alternative cost comparator: **OpenFHE BFV public-W** encrypted exact linear
evaluation, with the secret key held only by P0. Pin its encoding/plaintext
modulus to the same accumulator bound and clear every non-designated output
slot. This tests a different trust contract: library security notes describe
IND-CPA/semi-honest use, not malicious server correctness. It cannot pass the
malicious-peer gate without additional reviewed verification. P0 must not
return decrypted results/errors to P1 or expose a generic decryption oracle.
CKKS is deferred: approximate arithmetic, decryption-feedback and slot leakage
need their own analysis; do not transplant BFV conclusions. Source:
[OpenFHE security notes](https://openfhe-development.readthedocs.io/en/latest/sphinx_rsts/intro/security.html).

## Stages and preregistered pass/fail evidence

Every row is planned, not passed. One missing row blocks its own claim.

| Stage | Required observation / pass criterion | Failure or limitation |
| --- | --- | --- |
| A: algebraic oracle | Every fixture agrees exactly with signed wide-integer reference; checked bounds; both shapes represented | Any mismatch/overflow fails numerical implementation. Plaintext or simulated timing proves no privacy. |
| B: real malicious backend | Exact reviewed backend/program/dependency/build digests; two isolated parties; real preprocessing; all designated outputs exact; no output accepted before integrity checks | Missing backend/pins, skipped checks or insecure preprocessing blocks secure execution evidence. |
| C: corruption/dropout | Reviewed local fault hooks corrupt a share/MAC or preprocessing artifact, close either party, truncate/reorder messages and replay an expired task; each produces correct allowed result or explicit bounded abort, never accepted wrong result | One accepted wrong result fails integrity. Transport corruption tests alone do not exercise malicious protocol behavior. Bounded fixtures cannot prove the security theorem. |
| D: leakage/output review | Verify P1 has no plaintext X/Y path; only designated output released to P0; allowlisted metadata only; secret-W range leak explicit; no debug share/key export | Undeclared opening, extra BFV slot, decryption oracle or plaintext fallback fails. Logs/packet inspection alone are not confidentiality proof. |
| E: lifecycle | Public task/program/profile digest binding, same ID/same request handled without preprocessing reuse; changed digest rejected; timeout/cancel discard backend state; restart creates fresh crypto context | No checkpoint resume until proven safe; no arbitrary peer code; RFC-0002 adapter remains future implementation. |
| F: cost | Record compile/setup, real preprocessing, input sharing/encryption, online evaluation, integrity checks, reconstruction/decryption and end-to-end separately; both parties' wall/CPU/RSS and traffic | Online-only figures cannot claim total throughput. BFV/MPC confidentiality/functionality differences remain labelled. |
| G: target/utility | Actual Android owner plus Linux peer measurement on named hardware; paired local baseline; owner CPU, total latency, memory and energy evidence where supported | ARM64 host support or host simulation is not Android support. No identified phone/backend/harness means blocked target feasibility. |
| H: qualified review | Independent qualified reviewer maps exact implementation/parameters/output/composition to assumptions and recorded results | Lab success never approves a registry entry or release automatically. |

For C, propose timeout 120 seconds per trial and abort cleanup within a further
5 seconds, memory stop at 1 GiB per party and aggregate traffic stop at 256 MiB
per trial. These are conservative synthetic-lab stop budgets chosen for bounded
execution, not product performance promises or measured feasibility. Record
which limit fired; exceeding it fails that candidate/configuration budget.
Host resource controls must actually enforce bounds before hostile hooks run.
Do not expose the fault-injection binary to production or personal data.

For F/G, plan three warmups and 30 recorded paired local/secure runs per shape,
variant and topology; report all failures, raw non-sensitive scalar observations,
median/p95 and sample count. Compare cold setup-inclusive and warm per-request
cost, including an explicitly finite fresh-preprocessing budget; no hidden
unlimited cache. Initial topologies: same-host two-process (harness only),
two-host LAN, then actual Android owner/Linux peer. Pin measured RTT/bandwidth,
CPU scheduling, threads, power/thermal state and network conditions. Simulated
latency gets a simulation label and never a real-device label.

An offload-utility claim passes only when, for the same exact operation/input
contract on the named phone, paired evidence supports both lower owner CPU and
lower complete latency than local execution, with declared uncertainty intervals
excluding parity; otherwise record no demonstrated benefit. Thirty trials do
not certify tail reliability, thermal sustainability or model-level accuracy.
If energy instrumentation is unavailable, energy benefit is blocked rather
than inferred from wall time. Select no protocol merely from fastest simulated
online time.

## Reproducibility and execution blockers

Before any secure trial pin full upstream commits, dependency/submodule
revisions, compiler/flags/architecture, protocol binary and program hashes,
field/OT/MAC/security parameters, fixture generator, output policy and transport
configuration. Pin OpenFHE scheme, security setting, ring dimension, plaintext
and ciphertext moduli, packing, key-switch/rotation choices and slot mask.
Do not fetch mutable upstream main during a recorded run. This research did
not resolve/download/build immutable backend revisions; that remains explicit
work before execution. Mutable documentation below is a dated research source,
not a dependency lock or production recommendation.

Forbidden as secure evidence: `Fake-Offline.x`, `-DINSECURE`, dealer-generated
known shares, skipped MAC checks, semi-honest substitution, or merely running
both parties in one trusted process. MP-SPDZ distinguishes real preprocessing
from insecure online-only benchmarks; its documentation also cautions that
protocol availability is not production code security review. Its documented
ARM64 examples do not establish Android support. See
[MP-SPDZ execution and benchmarking notes](https://mp-spdz.readthedocs.io/en/latest/readme.html)
and [designated-party reveal API](https://mp-spdz.readthedocs.io/en/latest/Compiler.html#Compiler.types.sint.reveal_to).

Evidence entry per attempt: WORK/run ID, source commit/dirty snapshot, immutable
inputs/config hashes, exact commands, host/platform/device, exit/signal/status,
sanitized scalar metrics and failed gates. Capture no prompts, tensors,
shares, keys, identifiable training data or raw backend logs by default. The
WORK-0002 provenance collector can record inventory; it does not itself prove
that a secure operation ran. Registry change, actual authenticated distributed
adapter and qualified profile approval are distinct future bounded changes.

Research accessed official sources on 2026-10-22. No external publication,
backend installation, model execution, secure experiment or benchmark occurred
in this preparation run.
