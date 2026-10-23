# Reproducible phone benchmark collection

WORK-0002: primary active work; Samsung Galaxy A72 selected by owner. Exact
properties must come from a real connected device. The collector is not an
inference engine, exporter, phone simulator or approved privacy backend.

## Inventory and native measurement helper

Enable Developer options/USB debugging and approve this PC on the unlocked phone.
ADB Platform-Tools37.0.1 is pinned in config/development-windows.json and its
SDK license extension was explicitly approved. Use a single authorized device;
if necessary select one via ANDROID_SERIAL in the environment. Its value remains
in memory and is not printed or included in reports. No accounts/logcat queried.

```text
python tools/phone_benchmark.py probe --output .artifacts/phone-benchmark/probe-NEW/report.json
python tools/phone_benchmark.py build-helper --output .artifacts/phone-benchmark/helper-NEW/bench_exec
python -m unittest discover -s tests -p test_phone_benchmark.py -v
```

Use the explicit Python3.12 executable on this Windows host if the Store alias
does not work. Outputs are exclusive and confined under .artifacts; use a fresh
path for every attempt. Probe errors are retained as sanitized blocked reports.
Helper cross-compilation uses the existing NDK27/API26 ARM64 clang, warnings as
errors. A successful compile is not helper execution or model compatibility.

## Runner and recipe preparation

Resolve source/runtime files against config/model-baselines.json and the model
research handoff. No ready CPU export/runner pair is claimed. The pinned legacy
Qwen export path currently reaches torch.save/load; use only a reviewed
safetensors-only adapter, not automatic pickle loading or remote model code.
Export quality/reference comparison and runtime operator placement remain gates.

After a reviewed .pte, tokenizer, public synthetic fixture, native llama_main
and bench_exec exist, provision their exact bytes to
/data/local/tmp/p2pllm-benchmark/. Model execution is local synthetic-only;
the tool does not push executable files or download models automatically.
Each of the five recipe artifacts has local_path, remote_path and sha256;
the local and on-device bytes must both match. Distinct basename-only remote
paths are enforced; model must end in .pte. No shell operators/traversal allowed.

Recipe schema_version1 has exactly these keys: model_id, model_revision (40hex),
runtime_revision (40hex), quantization, export_config_sha256 (64hex),
requested_backend, trials (3..10), max_new_tokens (2..512), cpu_threads (1..16),
timeout_seconds (1..1800), artifacts. Artifacts has exactly launcher, runner,
model, tokenizer, fixture; each has exactly local_path/remote_path/sha256.
No prompt text, arbitrary custom metadata, or generated output in recipe/report.
Pinning is provenance, not independent evidence that a graph uses a backend.

```text
python tools/phone_benchmark.py run --recipe .artifacts/phone-benchmark/recipe.json --output .artifacts/phone-benchmark/run-NEW/report.json
```

Every trial launches a fresh process without model warmup. OS page cache is
uncontrolled: neither first nor later trials prove cold cache. No cooldown is
inserted; repeated trials retain order, failures, battery temperature and any
available thermal/power status before/after. Unknown telemetry is null, not zero.
No root, clock forcing, thermal disabling, or unrelated process termination.

## Metric meaning and limitations

The source-pinned runner emits PyTorchObserver JSON. Only required numeric fields
are retained; stdout prompts/generated text and stderr are discarded. The
collector caps total output2MiB and line64KiB; duplicate/missing/nonfinite or
inconsistent records fail. Fixtures/unit tests never count as phone benchmarks.

- Load: model_load_end_ms minus model_load_start_ms.
- TTFT: first_token_ms minus inference_start_ms, excludes load. At this pinned
  revision the endpoint precedes tokenizer decode/callback, so it is internal
  runner latency, not time to first text arriving at the host.
- Runner decode throughput: generated_tokens divided by inference_end_ms minus
  prompt_eval_end_ms, converted ms to seconds. generated_tokens excludes the
  first token generated during prefill and counts EOS reached by the decode
  loop. It is not the requested max_new_tokens or total visible output length.
- Observer clock is upstream CLOCK_REALTIME on Android; backwards/inconsistent
  timestamps fail. Launcher wall duration uses CLOCK_MONOTONIC separately.
- Peak RSS: waited child wait4 ru_maxrss, KiB; not sampled PSS, GPU allocator
  memory or the sum of an arbitrary process tree. Helper always supplies a real
  timeout and targets only its owned child group, TERM then KILL. USB loss does
  not guarantee immediate cancellation; remote deadline still bounds the run.

Current run status deliberately remains incomplete even if all numeric trials
are observed: actual_backend is unverified until independent graph/delegate
placement evidence is implemented/reviewed. Requested CPU/XNNPACK is not proof.
Exit0 means inventory observed; run incomplete/blocked returns2, tool error1.
No phone-performance, accelerator or privacy acceptance from these tool tests.

Primary sources: [pinned runner statistics](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/stats.h),
[runner token timing](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/text_llm_runner.cpp),
[runner clock](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/util.h),
[wait4 resource accounting](https://man7.org/linux/man-pages/man2/wait4.2.html),
[Linux maximum RSS units](https://man7.org/linux/man-pages/man2/getrusage.2.html).
