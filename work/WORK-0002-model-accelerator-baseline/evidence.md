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
