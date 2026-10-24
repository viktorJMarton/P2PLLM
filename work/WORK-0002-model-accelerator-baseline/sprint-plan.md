# Phone inference feasibility sprint

Run: run-20261022-phone-baseline-01; baseline ba6b116; development branch
work/WORK-0002-phone-baseline. Owner accepted this scope on2026-10-22.

## Priority and outcomes

1. WORK-0002 model measurement has first claim on capacity. A reproducible phone
   baseline reduces the primary feasibility risk. UI/ledger integration waits.
2. WORK-0003 prepares one precise privacy experiment, with threat model and
   success/failure criteria committed before execution. Preparation is not a
   completed feasibility experiment or approved privacy profile.
3. Minimal Android/Rust/SQLite integration is deferred if it competes with1.

Target: Samsung Galaxy A72, replacing the initially offered Honor400Pro.
Exact model/SKU, actual RAM, OS/build/API and ABI must be read from the device;
do not infer them from product-family specifications or 'latest system'.
No permanent device serial, account identifiers or personal prompts in evidence.
Owner approved Platform-Tools SDK license extension in this session; pinned
Windows package37.0.1 installed after official metadata/hash verification.
Initial ADB probe found zero attached devices; this is not a hardware result.

## Measurement contract

Pin model repository+immutable revision, tokenizer and source artifact hashes,
model/exported-artifact hash, quantization scheme and export parameters, runtime
source revision/build flags/binary hash and actually used backend. A requested
GPU/NPU/backend flag alone is not placement proof; mixed/fallback use is explicit.
Start with0.6B CPU; gate1.7B on actual0.6B memory headroom rather than estimates.

Record raw numeric observer timing fields with units and definitions, not raw
runner output. Load=end-start; TTFT=first generated token minus inference start,
excluding model load; throughput names its token count/time interval exactly.
Peak resident memory is kernel process high-water RSS if available; sampled PSS
is distinct and cannot silently substitute. Unknown metrics remain unavailable.
Three or more consecutive trials, fresh process per trial, identical public
synthetic fixture and fixed generation policy; preserve failures/order and all
samples. Fresh process does not establish a cold OS page cache. Capture battery
temperature and available thermal status before/after; do not claim thermal
throttling solely from token-rate changes. No forced clock/cache/thermal bypass.

## Acceptance and limits

Measurement tooling tests/builds may complete without a phone. Phone benchmark
acceptance requires actual execution on the identified device, all minimum
metrics/provenance and independent evidence review. Missing export/runner,
backend proof or USB authorization remains an explicit blocker. No CPU simulator
or host unit test is relabelled Android or private AI evidence.
Model reference/export numerical-quality comparison remains WORK-0002 scope;
performance data alone does not pass model equivalence or accelerator support.

Implementation/checkpoint closure follows AGENTS.md: checks, independent review,
commit, appropriate branch push and remote SHA check. Upload a new APK to the
owner's Drive structure only if a new APK was actually built; this tooling sprint
does not require rebuilding an unchanged UI to create an artificial artifact.

## Active continuation 2026-10-23

Run run-20261023-export-runtime-02, baseline42b4a0c, same developmentbranch.
Deliver actual pinned0.6B CPU inference and three numericA72 trials: guarded
export (sqlite-layer), matchingnative runner (primary), reviewed artifactstage
(phone-staging), independentreview on changedcode/results (product-review).
No UI/doc-only expansion. Preserve numerical/backend/measurement gates and
three-iteration meetings; use short delta logs/targetedreads/checks. Native
sources in separate .artifacts/native/executorch so exportcheckout stays fixed.
