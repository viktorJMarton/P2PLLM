# Model research handoff

- WORK: WORK-0002; run: run-20261022-model-research-01.
- Agent: android-shell; primary role/persona: qwen-research-deputy /
  Revision-disciplined upstream research deputy. Prior UI responsibility is
  superseded by this explicit research assignment; counters continue.
- Journal/integration owner: primary. Branch: work/WORK-0002-phone-baseline.
- Base: ba6b116f15567ba0469040ff1b73542e57d7f71c; source uncommitted.
- Research-owned paths: docs/models/qwen-baseline.md,
  config/model-baselines.json, this handoff, own android-shell journal.
- Status: research source/hash verification delivered; export/phone acceptance
  blocked until safe loader, dependencies, actual build and measurement evidence.

## Delivered scope and provenance

[Model baseline](../../docs/models/qwen-baseline.md) describes exact model and
runtime pins, CPU recipe, runner CLI/JSON/count/clock semantics, official source
limits and concrete next steps. [Manifest](../../config/model-baselines.json)
contains two immutable HF commits, seven separately hashed non-weight files
per model, complete retrieved HF architecture config, immutable ExecuTorch
source hashes and metadata-only candidate host wheel URLs/SHA-256 values.
UTC access start: 2026-10-22T18:00:18.289506+00:00; later same-run source/metadata
fetches appended before freeze. No model weights, runtime install/export,
SDK/license changes, phone benchmark or executed-delegate proof in this slice.

0.6B revision c1899de289a04d12100db370d81485cdf75e47ca; 1.7B revision
70d244cc86ccca08cf5af4e1e306ecf908b1ad5e. Both separately retrieved LICENSE
files hash to832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e.
ExecuTorch v1.5.1 source commit3b60683923245cf472b7323426920e15623ba361 is a
candidate research pin, not an installed dependency upgrade.

## Material findings and handoff decisions

- First target owner-reported Samsung Galaxy A72, exact ADB inventory pending.
  0.6B CPU/XNNPACK8da4w first;1.7B only after measured0.6B memory. No Honor
  performance/SKU claim carried forward.
- Official Qwen recipe exists for both sizes but uses a legacy checkpoint
  conversion path with torch.save/torch.load and unpinned automatic HF download.
  A separate safetensors reader exists but is not wired into that recipe.
  Under AGENTS.md this unmodified automatic loader is blocked.
- Reviewed repair proposal: explicit local immutable safetensors checkpoint,
  safetensors load plus pinned Qwen key mapping in memory, no pickle/network,
  no LoRA/QAT/SpinQuant/prequant branches. No implementation claimed here.
- Source recipe context2048 differs from model HF metadata40960. NDKr28c tested
  upstream differs from already approved projectr27: no silent upgrade.
- Windowscp312 wheels are listed in official PyPI metadata, but compatibility,
  native operator availability and complete transitive/hash lock remain untested.
  Windows source guidance requires VS2022+Clang-CL; MSVC alone is insufficient.
- No matching official prebuilt Android runner+CPU Qwen PTE established by
  release asset/executorch-community metadata queries. WebGPU export and
  unchecked third-party artifacts are no fallback for this CPU measurement.
- PyTorchObserver JSON stdout is machine-readable, but raw output contains
  prompt/generated text. Collector must allowlist stats only, not persist logs.
  generated_tokens excludes the prefill first token; clock is CLOCK_REALTIME,
  not monotonic. TTFT precedes decode/output callback and excludes model load.
  RSS is not in JSON; separate kernel/waited-child or accessible proc metric
  provenance is required. Human RSS logs are point samples, not peak proof.

## Observed verification

Windows/Python3.12 urllib metadata/source scripts computed SHA-256 from exact
downloaded bytes, exit0 after authorized network escalation. Initial sandbox
network WinError10013 provided no successful retrieval (script itself exit0).
One source-print command failed cp1250 encoding exit1; UTF-8 retry succeeded.
Neither failure was hidden or construed as successful verification.

No official upstream code executed. No PTE/APK/runner package or publication
produced. Final combined docs profile, source inventory and independent review
belong to primary after writer freeze; this research cannot close WORK-0002.

## Journal meeting and lesson references

Own [journal](../agent-journals/android-shell.md) iterations4 onward records
actual sources, role transfer, failures and current peer questions. Three/five
meeting policy remains in force. LSN-001/004/006/007 apply: named provision
blockers, frozen checks, no research-as-measurement, reviewed branch push owned
by primary. Pending peer answers do not authorize contract/release changes.

## Next bounded assignment

Primary subsequently authorizes tools/export_qwen.py + meaningful loader safety
tests and a pinned isolated upstream patch, followed by isolated venv dependency
resolution. Before implementation, researcher completes current actual peer
meeting. Safe-loader source delivery/testing must remain distinct from actual
successful export, numerical comparison, phone inference or qualified privacy
review. Primary owns collector/device; researcher owns export wrapper; independent
reviewer reviews exact delivered source and evidence. No llama.cpp/main fallback.

## 2026-10-23 safe-export source and provisioning progress

Subsequent authorized tools/export_qwen.py and tests/test_export_qwen.py now
implemented. Python3.12 final targeted run15/15 passed, exit0: synthetic safety
tests, not a model benchmark. Actual pinned source transforms compile; reviewer
independently inspected mapping/missing-weight logic. Full import readiness open.

Isolated venv created. Four-pin wheel-only resolver first failed: Hydra requires
ANTLR4.9.* without upstream wheel. Reviewed BSD4.9.3 setup/source and built only
this exact pure-Python wheel with setuptools77.0.3/wheel0.45.1; hashes in manifest.
Project-scoped pip cache fixed an initial permission failure, preserved in journal.
Resolver003 exit0:60-package exact hash lock/inventory recorded;60 wheels downloaded.
ET/torch installation/model export not yet performed in this entry.

Fixed interrupted-provenance and full trusted-lock/installed-closure findings;
Python network/pickle guards are defense in depth, not an OS sandbox. Default
prepare validates inputs and isolated patch only; --execute needs dedicated venv,
complete lock and actual checkpoint. Raw export output suppressed. Backend/device/
reference/privacy acceptance separate; no validated PTE exists yet.

Own journal Meeting9 records actual receipts/questions and15-test evidence.
Wrapper source frozen for independent recheck; next own work authorized license
inventory/hash-locked install/immutable checkpoint bytes. Primary owns actual
device/collector and reviewer owns affected safety/final source review.

## Current frozen export prerequisite checkpoint, 2026-10-23

Source wrapper/tests now16 targeted tests pass, exit0. Wrapper verifies official
Windows wheel raw artifact/member hashes and canonical LF upstream source,
adapts only dedicated-venv files and validates actual installed import paths/
effective hashes. Exact source hashes are in own journal iteration11. Entrypoint
and checkpoint audit files now fetched; no silent source/main/runtime upgrade.
Git lazy fetch disabled inside preflight; missing sparse metadata first caused
a preserved failure, retrieved during explicit setup, then prepare passed.

Actual isolated60-package install succeeded from full hash lock; pip check and
installed default-extra RequiresDist closure60 checks passed. License inventory
records221 members, no redistribution legal approval claimed. Exact0.6B public
safetensors1503300328bytes and7metadata files downloaded and size/SHA verified
after117GB disk preflight. Weights have **not been loaded** by this checkpoint.

Actual wrapper default prepare passed; exact source patch and installed-wheel
adaptation passed without model imports. Evidence directory
.artifacts/exports/qwen-prepare-20261023-002/ contains export-provenance.json
(prepared_not_exported) and installed-source-records.json (13 verified source
members). No PTE, numerical equivalence, successful native operator import,
device inference, backend placement or privacy claim yet. Independent affected
source review precedes actual execute; source is now frozen for combined checks.
Parent may close its separately verified diagnostic checkpoint while this WORK
remains in_progress. Next own step is actual guarded import/export after review,
with any genuine missing native module/dependency reported as its named blocker.
