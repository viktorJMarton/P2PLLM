# Guarded export configuration/preload diagnosis handoff

- WORK / runs: WORK-0002; run-20261023-export-config-probe-01 and
  run-20261023-export-preload-probe-01.
- Agent / role / persona: sqlite-layer / research / Reproducibility-first
  technical investigator. Earlier Rust authorship remains separate; no claim of
  independent approval of own runtime.
- Integration/journal owner: primary; implementation owner remains model agent.
- Branch/source: work/WORK-0002-phone-baseline, baseline
  ba6b116f15567ba0469040ff1b73542e57d7f71c, uncommitted combined source.
- Status: read-only diagnosis complete; actual export failure cause unresolved.

## Verified observations

Original export worker result states failed/export_pipeline without a reason.
That result does not identify a configuration error, weight-load completion or
native failure. No production wrapper, config, tests or installed source changed
in this investigation. Only ignored probe files/reports were created while
primary's final Android checks held a source freeze.

Actual commands using .artifacts/venvs/qwen-export/Scripts/python.exe:

| Probe command suffix | Exit | Observation |
| --- | --- | --- |
| `.artifacts/exports/config-probe-20261023-001/probe.py original` | 0 | Original export_arguments reach actual Hydra/OmegaConf main and one no-op export call; configuration valid |
| Same script `no-plus` | 0 | Probe reports ConfigCompositionException/base.model_class, zero export calls; stripping '+' would introduce a defect |
| `.artifacts/exports/config-probe-20261023-001/preload_probe.py` | 0 | Actual installed pipeline reaches explicit safetensors pre-load sentinel;13 installed source hashes match |

Exit0 for the negative control means the diagnostic script recorded its expected
failure; it does not mean the altered exporter arguments succeeded.

Windows/Python3.12 dedicated hash-locked venv, torch/imports from its installed
trusted code. Wrapper SHA256
A09EA6A71E1B4B5F337D2E9380A75D7192F6719E7AB22FE86B5F22F827C21DD2;
installed entry SHA256
D2ACE4DCF60538D90C4EB28068DB7E7098DC37244FB1E90ED1CE051A120D3480.
Model target remains Qwen3-0.6B c1899de289a04d12100db370d81485cdf75e47ca,
ExecuTorch3b60683923245cf472b7323426920e15623ba361. No package changes.

Preload probe uses HYDRA_FULL_ERROR=1, original config and argument generator,
same checkpoint/output parameters. Guards deny torch.load/save, checkpoint
open/safe_open and network; safetensors.load_file raises a named sentinel before
reading weights. Counts: sentinel1, forbiddenserialization0, forbiddennetwork0.
Code reaches Llama2Model.__init__ then _qwen_load_safetensors; no loaded model,
checkpoint tensors, PTE export, reference equivalence or inference is established.

Reports contain bounded status/class/count fields and static traceback
filenames/functions/line numbers only. Python warning/diagnostic text was held
in memory and discarded; no raw exception messages, locals, prompts or tensor
values persisted. Guards are defense in depth on reviewed pinned code, not an
adversarial Python/native OS sandbox.

## Evidence references

Ignored directory: .artifacts/exports/config-probe-20261023-001/.
Exact-byte report SHA256:

- original-report.json:
  B42A55AF897AB04212C82B658D88A0F05EC707BFD1446C2218C38AD5337E6325.
- no-plus-report.json:
  F7D906020617201597C5B0BBF1E7EC192DB1AF1DF92925C2945ED3E5790205C8.
- preload-report.json:
  C2C22238894F9EA84F19B11AA362FCED7DFFAE2BFE3669086AA01626CF6F8766.

## Diagnosis and next owner

Do not change working '+' overrides based on an unverified Hydra hypothesis.
The configuration and pre-load path passed these bounded checks. Original
failure could occur deeper or depend on original execution state; exact cause
remains unknown. Missing reason is consistent with SystemExit escaping the
worker's except Exception, but does not locate the original failure.

Recommended primary/model-owner next action: a fresh authorized guarded actual
export attempt with HYDRA_FULL_ERROR=1 and reviewed bounded exception-type/static
frame capture. Capture exact failed stage without raw payload/error logging.
Any production wrapper repair needs affected tests/review; this investigation
applied none. Loaded-weight/export/backend/device/model-utility gates remain open.

## Journal meeting and lesson references

[Own journal](../agent-journals/sqlite-layer.md), iterations7/8 appended only
after primary explicitly lifted journal/handoff freeze; prior actual meeting6
contains at least5 owned questions/peer receipts under
[meeting rules](../../docs/operations/agent-meetings.md). Counter did not reset
on persona/WORK transfer; next meeting due after iteration9 before10. LSN-004
source freeze and LSN-006 source/config probes versus actual measurements apply.
Current notes freeze again for final combined docs/source verification.

No package/publication/commit/push performed by this department. Primary owns
final applicable checks, independent review, commit, development-branch push and
remote SHA verification. This read-only diagnosis is not completed model work.

## Superseding actual retry and logging correction, 2026-10-23

After the above no-load probes, primary authorized ONE actual guarded export.
Ignored launcher reused existing source/dependency/serialization/network/job
guards,1800s timeout, same model/adapter/pins and raw consoledevnull. Preflight
rejected generated Hydra outputs before worker start; preserved failure and
quarantined that known directory without weakening source checks. One actual
worker then reached safetensors load_completed=true; no PTE/result established.

Concrete pinned builder.py lines216/217 INFO inputs/kwargs plus default Hydra
FileHandler exposed a logging defect. Controlled stop killed only verified own
worker21300, parent WindowsJob cleanup completed, known worker/stub remaining0.
Launcher recorded export_process_failed; original deeper export exception is
UNKNOWN, because this retry was deliberately stopped for the separate hazard.

**Correction:** initial log0B was a momentary observation. After stop, both current
and prior-quarantined export_llm.log were4435B with actual tensor repr/input/
kwargs markers. In-memory classification printed no raw values; removed exactly
these two raw logs and retained only sanitized classification/disposal evidence.
Do not claim never-logged, stopped-before-logging, global no-leakage or successful
export. Reviewer withdrew previous further-execution no-blocker until repaired.

Ignored evidence now includes logging-containment-report.json,
actual-retry-launcher-preflight-report.json, actual-retry-launcher-report.json
and qwen-exec-diagnosis-20261023-001/diagnostic-worker.json/export-provenance.json.
Own iteration9/meeting9 has actual peer receipts and5 new guard questions. Next
authorized work is tools/export_qwen.py plus its tests only: robust process-level
logging suppression, explicit Hydra logging disabled, bounded error type/static
frames; no new actual export before affected independent review.

## Focused logging repair delivered for independent review

run-20261023-export-logging-fix-01; primary-authorized two-file patch:
tools/export_qwen.py and tests/test_export_qwen.py. Pre-import logger/handler
emission guard survives Hydra reconfiguration, plus explicit disabled Hydra
job/hydra logging, no output metadata subdir and ignored run directory. Existing
pins, safe adapter,60-package closure, serialization/network and process/job
cleanup unchanged. Upstream fstrings still evaluate in memory; this is a
trusted-Python logging persistence boundary, not native/direct-file sandboxing.

Bounded error type/static frame chains (max5 chains,20 retained frames each)
exclude messages/source/locals/SystemExit code; only exact allowlisted ExportError
reason codes pass. Worker handles SystemExit explicitly. Additive error_details
does not relabel failed execution as successful preparation/export.

Observed `python -m unittest discover -s tests -p test_export_qwen.py -v` exit0,
19 tests. Logging mutation isolated in subprocess tests; no host Hydra dependency.
Real installed-venv Hydra no-model probe also exit0/passed, report
.artifacts/exports/logging-probe-20261023-001/report.json:60 closure,13 source
checks, exact builder bytes verified against official wheel; real input/kwargs
logging sites exercised with fake graph exporter, no model load. Synthetic
canary absent, late/direct handler files empty, no Hydra log/metadata directory.

Frozen wrapper SHA256
23197A3A35FC98BD9440B19CF8E2B96EF4BE516B691E1817F614E7045AB45B6C.
Own journal iteration10 records scope and actual meeting9 answers. Independent
review requested; no next actual export until affected review/checks and primary
scheduling. Earlier4435B retention/disposal correction remains authoritative;
new canary success does not erase historical leakage or certify arbitrary code.
