# WORK-0002 journal

No implementation activity recorded. Brief creation is planning only.

## Run run-20261022-phone-baseline-01 — 2026-10-22

Started on ba6b116, branch work/WORK-0002-phone-baseline. Owner accepted capacity
priority and measurement minimum. Read PRODUCT/TECHNOLOGY, existing model and
architecture/security contracts, role/memory and briefs. Assigned model/runner
source research to android-shell, privacy preregistration to sqlite-layer and
independent acceptance/security review to product-review; separate owned files.
Target revised by owner to Samsung Galaxy A72. Integration intentionally deferred.

Provisioned approved Platform-Tools37.0.1 from Google repository2-1.xml metadata;
zip size8044989, official SHA1e03e78b1d80b396f1c3358e31251cb31740e1110,
SHA25645f4d63113e895ebde0c90f194099a4676b6ac653bd28d54314a9e022bbc1a99.
ADB1.0.41/version37.0.1-15733141 exit0; device listing exit0, zero connected
devices at first probe. Serial values are never printed/stored. Windows sandbox
CIM initially denied; elevated filtered probe found no matching phone entry.
No phone/model measurement yet. Current changes uncommitted.

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

### Real phone inference continuation

Observed three successful A72 inference trials; see [evidence](evidence.md#actual-a72-inference-checkpoint-2026-10-23-utc) and [portable observations](phone-observations.json). Native runner and recovered PTE are real; collector remains incomplete for numerical/backend gates. No new APK or in-app AI delivered. Primary owns quality/placement validation and Android integration next. Exact commit/push verification remains pending.

### Actual source delivery and review binding

Source commit60dd8afb647b01d881f7b9b70f4ea05713c91202, branch
work/WORK-0002-phone-baseline, independently reviewed by independent_review:
NO BLOCKER for bounded tooling/observations. Reviewer matched all six Git-blob
code/test hashes to prior independently reviewed snapshots, original evidence
hashes and all three metrics; no numerical/backend/app/privacy acceptance.
Actual gitpush exit0; subsequent ls-remote exit0 returned the identical source
SHA. This is the observed source delivery, not a future push claim. Metadata
follow-up records this result and fixes the stale brief sentence; its own
commit review/push remains pending until performed. Next primary owner keeps
WORK-0002 gates open and advances response quality/placement then Android use.
