# WORK-0002 independent measurement/security review

Reviewer: /root/product_review. Primary persona pr-review, security secondary
lens. Run RUN-20261022-PHONE-REVIEW-01. Initial source ba6b116f15567ba0469040ff1b73542e57d7f71c;
new sprint branch assigned by coordinator: work/WORK-0002-phone-baseline.

## Preimplementation acceptance risks

No phone benchmark or harness execution reviewed yet. Honor 400 Pro and
"latest system" are owner-reported context, not measured SKU/build/backend proof.
ADB availability/device permission remains unobserved by reviewer.

| Question | Risk and required distinction | Responsible respondent / status |
| --- | --- | --- |
| PHONE-Q1 memory | True process peak RSS/VmHWM differs from maximum sampled PSS. Preserve metric source, units, PID and sample interval; label sampled maximum honestly. Transient spikes can be missed; do not substitute free-RAM change for process allocation. | primary / open |
| PHONE-Q2 run state | Fresh process/model load, warm model session and OS page-cache state differ. Declare PID/process reuse, warmups, repeated measurements, model residency and cooldown/thermal state; process restart alone does not prove cold filesystem cache. | primary / open |
| PHONE-Q3 TTFT | Define time origin/end precisely: prompt submission to first generated token versus model load/startup. Separate model-load, prefill, TTFT and decode throughput; pin input/output token counts, EOS handling and measurement clock. | primary / open |
| PHONE-Q4 privacy | Device model/SKU/OS build/API and relevant RAM/backend fields suffice. Do not persist adb serial, device UUID, accounts, unrelated logcat or generated prompts/text. Redact command/error output, not merely final report fields. Use sanitized fixed fixtures. | primary / open |
| PHONE-Q5 actual backend | Requested backend flag/device SoC is not executed-backend evidence. Require runner/delegate placement evidence, record mixed CPU fallback and operation coverage, and mark unproven placement unavailable. Missing required evidence must not become a passing sample. | primary and android-shell / open |

Minimum reproducible sample also needs immutable model/tokenizer/export/runtime
revision, artifact hash, quantization configuration, exact runner and supported
operator/backend information. Repetition must preserve rejected/failed/OOM
attempts and count successful attempts without selecting only fastest results.
Record thermal/battery/charging/power state and uncertainty; unavailable thermal
signals are unknown, not zero or healthy. Parsed official runner stats remain
untrusted input: reject duplicate/ambiguous/nonfinite/negative/incompatible-unit
values and incomplete runs. A host parser unit test is not phone measurement.

Subprocess/ADB arguments need shell-safety review on both host and Android shell;
do not interpolate unrestricted paths/identifiers into remote command strings.
Bound captured output/timeouts, stop owned benchmark processes on cancellation,
and never kill unrelated device processes. Failed collection must retain a
sanitized failure outcome rather than fabricated metrics or overwritten evidence.

Final review pending delivered source, schema/fixture tests, actual measurement
evidence and exact commit. No private-computation conclusion follows from local
model capacity or accelerator benchmarking.

## Collector source review, initial implementation

Run RUN-20261022-PHONE-REVIEW-02, uncommitted sprint snapshot. Primary reports
owner changed target to Galaxy A72; actual device execution remains unobserved
by reviewer. Read tools/phone_benchmark.py, tools/android/bench_exec.c, its tests
and operational documentation. Python3.12 targeted test_phone_benchmark.py:
11 tests passed, exit0. C cross-build success is primary-reported; no native
helper or model run performed by reviewer. Source delivery is not phone evidence.

Blocking findings sent to primary for focused fixes:

1. **High, open — host cancellation:** collect_trial has no finally covering
   KeyboardInterrupt/reader/wait errors. Ctrl-C can leave adb/reader resources
   and remote execution alive, and bypass report serialization. Add bounded
   cleanup and explicitly sanitized interrupted attempt evidence.
2. **High, open — remote supervisor lifetime:** bench_exec traps TERM/INT only.
   Closing adb/pipe after host output cap or disconnect can deliver HUP/PIPE;
   helper can die while its runner has a separate process group, invalidating
   the claimed remote timeout guarantee. Trap disconnect-related termination
   into supervisor stop/reap behavior; test cancellation/disconnect and owned
   process-group cleanup. Do not claim immediate USB cancellation without proof.
3. **Medium, open — failure evidence durability:** main truncates the report
   before dumps; OSError or KeyboardInterrupt bypasses its MeasurementError-only
   inner handler and can leave empty/partial evidence. Preserve an initial
   attempt envelope and atomically replace complete checkpoints, with sanitized
   failure status on ordinary errors/interruption where possible.
4. **Medium, open — numeric overflow:** finite uses math.isfinite on arbitrary
   parsed ints. A bounded-size JSON integer such as 10**400 raises OverflowError
   instead of MeasurementError, escaping failure handling. Explicitly bound or
   reject overflow and add a regression.

Positive scoped observations: remote basenames are restricted and shell-quoted;
stat keys and output bytes/lines are allowlisted/capped; serial stays in memory;
unknown thermal fields remain null. Actual backend remains unverified and run
acceptance incomplete. Fresh process/pagecache distinction and pinned runner
CLOCK_REALTIME/token semantics are explicit. Kernel wait4 high-water RSS is an
appropriate waited-child metric, excluding GPU allocation and arbitrary tree sum.
No execution acceptance granted while lifecycle/failure findings remain open.

## Related WORK-0003 preparation review

Read experiment-plan.md and handoff-privacy.md. No blocking finding for a
proposed-only synthetic research plan. Public-W versus secret-W functionality,
input-range gate, exact accumulator bound, malicious/static assumptions and
full real preprocessing are explicitly separated. Exact backend/OT/MAC/field
parameters and consumption of output only after required integrity finalization
remain execution blockers. Registry stays approved-none; no crypto code,
privacy proof, target measurement or qualified cryptographic approval reviewed.

Consulted primary [MP-SPDZ API](https://mp-spdz.readthedocs.io/en/latest/Compiler.html#Compiler.types.sint.reveal_to)
and [OpenFHE security notes](https://openfhe-development.readthedocs.io/en/latest/sphinx_rsts/intro/security.html).
The designated-output API alone does not prove completion/finalization. OpenFHE
documents semi-honest use and non-designated inner-product slots; plan accurately
treats these as separate comparator/output gates. This is a bounded plan review,
not an implementation audit of either cryptographic backend.

## Collector fix recheck and initial export-wrapper review

Run RUN-20261023-PHONE-REVIEW-03; uncommitted sprint source. All four collector
findings above **resolved within reviewed scope**: host finally kills/reaps own
ADB process and joins reader, supervisor traps HUP/PIPE, failure checkpoints
replace complete fsynced JSON, and numeric bound precedes isfinite. Independent
Python3.12 test_phone_benchmark.py: 16 passed/exit0, including actual host-child
interruption/output-flood regressions and checkpoint failure preservation.

Reviewed historical helper-device-001/report.json: normal exit0, timeout124,
explicit HUP130, all passed on SM-A725F/Android14. Report source SHA256 matches
current bench_exec.c 7ADBF204556B15D60FA1A2C0B440403E0F545AA1FC8D0430D1C4D2DFC633C76D.
Helper binary reported 63b3df8b508321e3c611842672b0222547f117bc0f18fe5d5558aa886a5bd3be.
This is primary-run historical native-helper evidence, not reviewer-run device
execution, current connectivity, complete USB-disconnect cleanup, model benchmark
or GPU allocation measurement. Root reports current phone not connected/authorized.

Other reviewed exact-byte source hashes:
phone_benchmark.py 4CD0E5845792D9EA6BF06DD546226CF177DEC06CE631FB9D0676921603EAD767;
test_phone_benchmark.py 4DF31797E66815AEF7B93B8624059F8F434F3B0F57145DB19EDC03D6A940741C.
Final commit binding pending.

Read tools/export_qwen.py and tests/test_export_qwen.py; independent synthetic
test suite 9 passed/exit0. No model weights, upstream checkout, export environment
or actual export executed by reviewer. Exact model/source hashes, deterministic
loader patch, bounded paths and hidden raw exporter output are useful guards.
They do not establish successful export or equivalent logits.

Open export findings before execution acceptance:

- **High, dependency-closure prerequisite:** read_dependency_lock checks four
  candidate pins; WORKER checks only listed installed versions. An omitted
  installed dependency such as safetensors may execute unpinned. A syntactically
  hashed partial lock does not establish the claimed complete dependency closure.
  Resolve/review full transitive lock and validate executing dependency closure
  against it, including safetensors, before actual model loading.
- **Medium, interrupted status:** run catches ExportError/OSError/subprocess
  exceptions but not KeyboardInterrupt; its finally can persist
  prepared_not_exported after an interrupted actual export and partial artifact.
  Record interrupted/failed explicitly and retain safe bounded failure metadata.
- **Review gap:** current patch tests use synthetic source. Independently compile
  both transformations against actual pinned upstream bytes, inspect all reachable
  loader/import/export branches and worker guards before model loading. Real
  upstream raw fetch failed in reviewer browsing; model owner was asked for cache.

Worker audit hook is defense in depth on trusted pinned dependencies, not an OS
network sandbox; socket.connect/getaddrinfo guards do not cover every network
operation (e.g. sendto). Do not state universal no-network proof from those hooks.
Requested focused execution tests for dependency closure, interruption and guarded
network/pickle paths. No export execution approval is supplied by this review.

### Actual upstream transformation inspection

Model owner supplied .artifacts/upstream/executorch-3b60683923245cf472b7323426920e15623ba361.
Reviewer independently read actual model/export source and Qwen converter;
both exact-source hash checks and deterministic adapted compile succeeded,
without loading dependencies/model or writing the upstream checkout:

- model.py adapted SHA256 628184c9e5967998d7583e6c2ee3253305f20afaccdfdf89a081ec8d6a88fb28.
- export_llama_lib.py adapted SHA256 c766c46f8e7b24420fb5a439fc8b70f1527909c71128a42bb1d2a57d366f4d2f.

Actual original missing-weight checks remain in adapted source; the pinned
mapping uses shared token-embedding weight for absent lm_head.weight. The
actual entrypoint is listed by Git tree but absent in this sparse local cache;
git show attempted promisor fetch and failed network. Therefore syntax/loader
inspection gap narrows, but full entrypoint/import/worker execution remains
unverified. This does not resolve full dependency closure or interrupt findings.

## Final frozen exporter safety recheck

Exact wrapper SHA256 A09EA6A71E1B4B5F337D2E9380A75D7192F6719E7AB22FE86B5F22F827C21DD2;
tests SHA256 A091989DE912C4DF17587185F73ED0D2D66B0C15DC18369B2B95F2673FC53A2C.
Independent Python3.12 targeted test_export_qwen.py:16 passed/exit0.

Dependency finding **resolved for trusted isolated installation scope**: trusted
configuration binds full lock digest, exact60 package versions and wheel hashes;
lock rejects omitted/extra/mismatched entries. Worker walks installed default
RequiresDist closure, markers/specifiers, rejects unsupported URLs/extras, and
requires exact locked closure before model-library imports. Metadata checks are
explicitly not proof against tampering by the local OS/user.

Interrupted-status finding **resolved**: wrapper/worker record interrupted and
export_cancelled, CLI130; regression proves no prepared/success/PTE hash after
interruption. Network event defense includes connect/DNS/sendto/sendmsg/pickle;
raw exporter output discarded. Guards remain defense in depth, not OS sandbox.

Reviewed official-wheel adapter: exact full wheel hash, raw member hashes and
canonical upstream LF match are kept distinct; both installed patch targets are
validated before writes; backup/reprepare/drift checks retained. Dedicated venv
only, installed module origin/effective hashes checked, fully qualified
executorch entrypoint, no checkout PYTHONPATH override. This addresses prior
source-import routing gap. Actual prepare/install results remain model-owner
evidence; reviewer ran only synthetic safety tests and source inspection.

No remaining blocking source finding for a bounded guarded export attempt under
these enforced prerequisites. This does not assert successful torch/model import,
completed export, numerical equivalence, backend placement or phone inference.
Model/PTE/runtime results must be observed and independently assessed separately;
WORK-0002 benchmark acceptance remains open. Final commit binding pending.

## Newly identified export file-logging hazard (execution gate reopened)

Investigator reported, and reviewer independently confirmed in pinned installed
extension/llm/export/builder.py::_export, INFO calls format self.example_inputs
and self.example_kwarg_inputs. Hydra default FileHandler can persist these in
export_llm.log despite wrapper stdout/stderr discard. Previous source review
missed this in-process file-logging path; its no-blocker conclusion for further
export execution is withdrawn until focused guard review. This does not change
the independently delivered WORK-0014 diagnostic APK/runtime conclusions.

**High, open:** before any new export attempt disable/guard Python/Hydra logging
before imports/configuration, remove or safely intercept pinned payload-formatting
sites, and demonstrate a real logging/FileHandler regression cannot write raw
inputs/tensors/kwargs. Preserve exact adapted-source hashes and trusted wheel
identity. stdout/stderr discard alone is insufficient.

Diagnostics for original export failure must retain only bounded exception class
and static sanitized frames (module/function/line); no raw exception message,
locals, source-line expansion, tensor repr, prompt or training data. Guards must
not silently weaken pickle/network protections to obtain a more detailed error.

Primary/investigator report controlled owned-job stop before reaching the
logging hazard and a zero-byte file; reviewer has inspected source, not repeated
model execution. Preserve that bounded observation without claiming the whole
export pipeline never logged data in every possible path. No new PTE/numerical/
backend/phone benchmark success is inferred. Required next action is separate
affected code/tests review, then an authorized guarded attempt with honest phase
status and the same immutable model/runtime/dependency pins.

### Factual correction, 2026-10-23

Investigator/primary corrected the zero-byte/before-logging observation above:
after owned-child termination and parent-job cleanup, both current and prior
quarantined export_llm.log were4435 bytes. Sanitized in-memory classification
found tensor-representation and inputs/kwargs markers. The earlier zero-byte
reading was a stale intermediate snapshot; it does **not** establish stopping
before logging. Tensor-formatted input/kwargs content did persist in those logs.

Known scoped raw logs were removed without displaying or copying raw content;
retained evidence is the sanitized classification/disposal report at
.artifacts/exports/config-probe-20261023-001/logging-containment-report.json.
Investigator reports both owned PIDs terminated and no PTE. These are attributed
cleanup observations, not reviewer-run execution or global/secure-erasure proof.
Further actual export remains blocked until logging guard/tests are reviewed.

## Affected logging-guard review, 2026-10-23

Reviewed exact wrapper SHA256
23197A3A35FC98BD9440B19CF8E2B96EF4BE516B691E1817F614E7045AB45B6C
and tests SHA256 A3BE3B38638D327DEE93C9633D18D7517A84C0B1149B9E847BBACB562F232A29.
Independent Python3.12 targeted export suite:19 tests passed/exit0. No actual
model load/export executed by reviewer or authorized by this checkpoint review.

High file-logging finding **resolved for the identified pinned Python/Hydra
paths**: emission guard installs in worker before dependency/model imports and
intercepts logger, handler and direct Stream/FileHandler emission/formatting;
Hydra job/hydra logging groups disabled, output metadata disabled, bounded run
directory. Hydra resets/late handlers cannot re-enable tested emission paths.
Tensor fstrings may still evaluate in memory; arbitrary native/direct filesystem
writes are outside this Python guard and it is not an OS sandbox.

Bounded diagnostic review: exact ExportError type plus fixed reason allowlist,
no exception stringification; chain<=5 and20 static trusted frames each,
type/filename/function/line only, no messages/locals/source/SystemExit value.
Worker catches SystemExit separately and retains sanitized failure phase.
Existing serialization/network/source/closure/owned-job controls unchanged.

Independently inspected actual probe SOURCE at config-probe-20261023-001/
guarded_hydra_probe.py and logging-probe-20261023-001/report.json. It verifies
60 dependency closure entries,13 installed source records and builder raw bytes
against the trusted wheel; actual installed Hydra calls a model no-op, which
executes real builder _export INFO sites while only graph export is stubbed.
Probe resets logging, creates late/direct handlers and scans scoped files for
synthetic canary, requiring both logs0B and no Hydra log/.hydra. Report passed;
reviewer directly rechecked those two log sizes0B but did not rerun the venv probe.
This is functional no-model logging evidence, not a secure-backend/model benchmark.

No remaining blocking source finding for this bounded logging repair checkpoint;
final applicable docs/workflow checks and committed-byte binding remain pending.
The earlier actual4435B tensor-log incident and cleanup correction remain true
and are not erased by passing regression. No new actual model retry is included
in this checkpoint; export/PTE/numerical/backend/device acceptance remain open.
