# WORK-0002 evidence

No implementation, model benchmark or security evidence yet. Add reproducible commands/results when executed.

## Superseding preparation observations, 2026-10-22/23

Modelresearch resolved immutableQwen revisions/config/tokenizer/license hashes
and pinnedcandidateExecuTorch source in config/model-baselines.json; see model
handoff for actual upstream loader/token/clock limitations. Research is not
model/reference/export/numerical-quality/phone inference evidence.

Collector host regression suite16passed. Independent reviewer2026-10-23 reran16
and resolved4 earlier lifecycle/durability/numeric findings. Chelpercrosscompile
NDK27/API26arm64 succeeded; sourceSHA7adbf204556b15d60fa1a2c0b440403e0f545aa1fc8d0430d1c4d2dfc633c76d,
binarySHA63b3df8b508321e3c611842672b0222547f117bc0f18fe5d5558aa886a5bd3be.
Actual SM-A725F/Android14/API34/SM7125 inventory: OS-visible MemTotal5625888KiB.
probe003 initiallynullRAM due CRLF parser, fixed+regression probe004 observedRAM.
Actual nativehelper-device001 cases normal/timeout/HUP all3passed; sampleRSS
4752/4616/4724KiB, timeoutwall1042.679ms andHUP238.366ms. These are tiny system
command probes, explicitly native_helper_validation_not_model_benchmark.
Localreports .artifacts/phone-benchmark/{device-probe-004,helper-device-001}/report.json.
No device serial/prompt/tensor/rawrunneroutput logged.

2026-10-23 currentphoneprobe is blocked; prior physicalproof not relabelled as
currentapp/device validation. Exportwrapper synthetic9tests initiallypassed,
complete dependencyclosure+interruptedstatus reviewfixes inprogress. Modelagent
resolved60exactversion/hash dependencies in isolatedvenv; install/export outcome
not inferred. NoactualQwenmodel/PTE/inference throughput/TTFT/memory measurement
yet. WORK2acceptance remains open; no approved privacy profile or fakebenchmark.

## Observed guarded export attempt and diagnosis, 2026-10-23

Primary records actual model-agent attempt at
.artifacts/exports/qwen-exec-20261023-001/: export-provenance status failed,
reason export_process_failed; worker-result phase export_pipeline, no PTE.
Earlier statement weights-not-loaded applies only to preparation checkpoint;
failed execute does not prove whether weights were loaded. No phone inference,
backend placement, load/TTFT/tps/memory or numerical validation result exists.

Follow-up investigator sqlite-layer, unchanged production source, reports
.artifacts/exports/config-probe-20261023-001/: original Hydra +base.* config
reaches no-op export; removing + fails ConfigCompositionException. Actual
pipeline reaches explicit pre-load sentinel at safetensors.load_file,13 installed
source hashes match, no forbidden serialization/network. Sentinel stops before
tensor loading. Exact original export failure is still unknown. Next actual
retry needs sanitized exception type/static traceback, retaining guards and
process cleanup; no runtime/backend/quantization substitution. WORK remains open.

## Export attempt stopped for concrete logging hazard, 2026-10-23

Run run-20261023-export-logging-01, WORK-0002. Investigator's single retry passed
60dependency/source guards and actual safetensors loader returned. This is not
PTE/numerical/phone/backend acceptance. Pinned builder.py::_export lines216/217
contains unconditional logging.info f-strings for example input tensors/kwargs;
Hydra default INFO FileHandler writes export_llm.log. Investigator observed
current file0bytes (without reading payload), stopped only owned worker before
that export path, existing parent WindowsJob cleanup applies. Actual terminal
cleanup/result must be recorded by investigator; no successful export claimed.
Independent reviewer confirmed source hazard and withdrew prior no-blocker for
further WORK2 export execution until corrected/reviewed. Prior review covered
stdout/stderr discard but missed in-process file logging. WORK14 tested APK and
its delivered/source commits05768cc/3810a4f are unaffected.

Authorized next bounded change: pre-import logging emission guard plus explicit
Hydra disabled logging/output metadata policy, meaningful late-handler/actual
Hydra no-model canary regressions, sanitized bounded exception types/static
frames including SystemExit. Keep all hash/closure/serialization/network/process
cleanup guards. No second actual model attempt until affected independent review.
Implementation owner sqlite-layer after own meeting9, reviewer product-review
after own meeting15, primary integration/checks/push. No privacy guarantee follows.

### Dated correction superseding the earlier zero-byte containment claim

2026-10-23, after owned-job cleanup: investigator reports BOTH current and
prior quarantined export_llm.log were4435bytes. Bounded in-memory classifier
found tensor representation plus inputs/kwargs markers. No raw content or tensor
values printed into handoff. Therefore the earlier0B observation was only a
stale snapshot: stopping BEFORE any logging/no tensors ever persisted is FALSE.
Root explicitly corrected this claim to owner. Known scoped raw log files were
removed; sanitized classification/disposal report retained under ignored export
artifacts as logging-containment-report.json. No general no-leakage claim.

Known owned worker PIDs21300/15880 remaining0; existing parent WindowsJob cleanup
completed, wrapper failed export_process_failed. No successful PTE/inference.
This is an actual logging failure and cleanup, not a successful privacy test.
Independent reviewer informed; execution remains blocked until logging repair
and affected review. Public-model export example tensor logging is unacceptable
under repository policy even though no phone/private computation was executed.

### Affected logging repair review outcome

Independent product-review verified exact wrapper23197A3A35FC98BD9440B19CF8E2B96EF4BE516B691E1817F614E7045AB45B6C,
independently reran19 tests (exit0) and inspected actual Hydra probe script and
report (not merely an implementer summary). Real installed entry with no-op
model, official-wheel-verified builder input/kwargs logsites, Hydra reset,
logging.disable(0), late/direct FileHandlers and scoped canary scan passed;
files empty/noHydralog. Specific trusted Python/Hydra logging execution blocker
resolved; no remaining blocking source finding in this repair. Prior incident,
raw-log disposal and dated correction remain recorded. No OS/native sandbox,
model export/PTE/numerical/backend/phone acceptance follows. Root final frozen
workflow/docs checks and source commit/push are next. No actual model rerun in
this bounded repair checkpoint; next WORK2 owner resumes reviewed guarded export
then numerical/runner/backend/device validation, not unsafe fallback.

### Frozen integration checks, logging-final-001

Windows11/Python3.12.0. Common docs profile exit0:665packagechecks plus agent
meeting policy pass. Common workflow profile exit0:68tests/67pass/1Windows
symlink privilege1314 skip. Reports under
.artifacts/checks/WORK-0002/logging-final-001/{docs,workflow}/report.json.
Stable canonical source fingerprint: 8fc8fe78e0db1d10941f4272f4852a606cda385cfa4bb550eb27efdc3b1f7f5a.
Observed source dirty on3810a4f; these reports identify pre-commit source,
not a rerun against a future commit. Rust/Android code/config/artifacts unchanged
since previously reviewed05768cc; no redundant product rebuild performed.
Independent affected logging review passed exact code and19targetedtests/probe.
This log continuation is metadata only; final docs inventory/check and exact
source commit binding/push remain to follow. Model export is NOT rerun or passed.

### Actual reviewed repair push and handoff receipt

Branch work/WORK-0002-phone-baseline; exact source commit
058c55fac095473308b5cdbe571f81351b02fa90 independently bound by product-review:
NO BLOCKER for bounded development checkpoint; wrapper/test hashes match and
Android/Rust/config unchanged versus3810a4f. Actual gitpush exit0; subsequent
ls-remote exit0 returned058c55fac095473308b5cdbe571f81351b02fa90, equal sourceSHA.
This is observed synchronization, not planned push or AI/privacy acceptance.
Metadata follow-up records this already-observed source push; its own finalpush
and remoteverify happen after finalscopedreview. Continued administrative record
of iteration19; no new model/code development or counter reset.

Next responsible owner: primary assigns available model researcher to execute
reviewed guarded exporter with sanitized diagnostics, then pin/validate numerical
reference, PTE/tokenizer, matching Androidrunner and actual backend placement
before repeated A72 load/TTFT/decode-throughput/peak-memory/thermal trials.
Original failed export's exactcause remains unknown; guardprobe is not a model
export. No unsafe logging/pickle/runtime/backend fallback. WORK-0002 and privacy
WORK-0003 remain in_progress. No actualmodelworker remains running.

## Actual A72 inference checkpoint (2026-10-23 UTC)

[Portable sanitized observations](phone-observations.json) preserve all three
trials, device inventory, exact artifact hashes, recipe and source-receipt hashes.
Qwen3-0.6B revision c1899de289a04d12100db370d81485cdf75e47ca,
ExecuTorch revision3b60683923245cf472b7323426920e15623ba361,8da4w,4CPU threads.
Native ARM64 runner build and all five staged device hashes verified. Export
worker completed; parent output-location check failed. A separately verified
copy recovered the PTE without rerunning export or rewriting failed provenance.

| Trial | Load ms | TTFT ms excluding load | Decode tokens/s | Peak child RSS KiB |
| --- | --- | --- | --- | --- |
| 1 | 4070 | 567 | 21.642 | 1014616 |
| 2 | 1576 | 224 | 21.860 | 1014640 |
| 3 | 1568 | 230 | 21.679 | 1014516 |

Each child exited0 with63 decode-loop tokens; excludes the first prefill token.
Fresh processes; OS cache uncontrolled. A72 SM-A725F/Android14/API34,
USB connected, battery27.0-27.1C, reported thermal status0. Three short runs
cannot establish sustained thermal behavior. Peak RSS is wait4 child ru_maxrss,
not device/GPU total. No prompt or generated response is persisted in evidence.

Collector intentionally returns2/status incomplete: actual backend placement and
reference numerical/quality validation remain open. Static placement probe001
failed with a generated-accessor TypeError; no backend proof is inferred.
WORK-0002 remains in_progress; WORK-0003 privacy is unchanged. Android app
inference is not implemented by this tooling checkpoint; unchanged APK0.2.0
still provides local diagnostics. Next owner primary: numerical/response-quality
check and explicit placement evidence, then bounded Android local question/answer
integration with visible progress, cancel/error states and real-phone acceptance.

Independent product-review found no blocking issue in the exact exporter,
shared compiler, native build and staging source snapshots;22 exporter and20
phone tests passed independently. Exact latest-commit review/push is pending
until recorded below. No release or completed model-feasibility gate is claimed.

Final frozen checks: Windows11/Python3.12.0, tools/run_checks.py profiles docs and
workflow, WORK-0002/run sprint02-final-002: both exit0/passed; source fingerprints
stable within each run. Docs677 package checks plus journal policy; workflow75
tests (74passed, one Windows symlink privilege1314 skip). Reports under
.artifacts/checks/WORK-0002/sprint02-final-002/{docs,workflow}/report.json.
Applicable product source unchanged, so Rust/unchanged APK not rebuilt. Current
source uncommitted on42b4a0c. Final native helper incremental006 pending;005
runner was already built and actually executed on phone. Successor independent
reviewer available for latest source commit; final push still pending.

Native006 final shared-verifier recipe subsequently passed all six phases/exit0; runner SHA3e9c443f82d9765a74cc66ed29c2c5d650ffc34c744ac9c8e4c9430b19b44b71 unchanged from actual phone trials. Report .artifacts/native/run-20261024-006/report.json. No new model export or additional trials.

Execution note: outer PowerShell redirected-console session006 reported exit1; the Python receipt reports passed and all six actual phase subprocess exits are0. Do not relabel the outer exit as0. Artifact matches previously successful build005 and phone execution; this wrapper discrepancy remains noted, not a model/backend acceptance claim.
