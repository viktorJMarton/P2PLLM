# Qwen baseline and operator research

## Revision-bound research snapshot

WORK-0002 / run-20261022-model-research-01. Checked 2026-10-22 UTC.
Status: metadata/source verification only; no weights downloaded, export run,
runtime installed or phone performance measured in this research slice.
Exact-byte hashes, sizes, pinned download URLs and architecture configs are in
[model-baselines.json](../../config/model-baselines.json).

| Intended use | Official repository | Immutable revision |
| --- | --- | --- |
| Diagnostic baseline | Qwen/Qwen3-0.6B | `c1899de289a04d12100db370d81485cdf75e47ca` |
| Useful-mobile candidate | Qwen/Qwen3-1.7B | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` |

Each manifest entry separately hashes config.json, generation_config.json,
tokenizer.json, tokenizer_config.json, merges.txt, vocab.json and LICENSE.
Both retrieved LICENSE files are Apache-2.0, SHA-256
`832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e`.
This records upstream terms, not a new licensing choice. No weight SHA-256 is
claimed: weights were deliberately not fetched. A future export must separately
pin safetensors filenames/content hashes, exporter dependencies, PTE and runner.
[0.6B license](https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/LICENSE),
[1.7B license](https://huggingface.co/Qwen/Qwen3-1.7B/blob/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/LICENSE).

The two snapshots have identical tokenizer-file hashes. Config differences:
hidden size/intermediate size are 1024/3072 for 0.6B and 2048/6144 for 1.7B.
Both specify 28 layers, 16 attention heads, 8 KV heads and head_dim=128.
The declared HF context limit 40960 is not a verified mobile working set.
The recorded config field transformers_version=4.51.0 is upstream metadata,
not this project's installed/export dependency lock.
[0.6B config](https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/config.json),
[1.7B config](https://huggingface.co/Qwen/Qwen3-1.7B/blob/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/config.json).

## Candidate ExecuTorch release and export boundary

Research pin: **ExecuTorch v1.5.1**, commit
`3b60683923245cf472b7323426920e15623ba361`; official release metadata reports
publication 2026-09-23T16:58:34Z. This selects a reproducible source candidate;
it does not silently upgrade installed project dependencies.
[Release](https://github.com/pytorch/executorch/releases/tag/v1.5.1).

The pinned Qwen3 example provides model classes qwen3_0_6b/qwen3_1_7b and a
CPU/XNNPACK 8da4w export recipe. C++ uses llama_main; HF tokenizer.json is
accepted and the caller must apply the chat template. Use the pinned
tokenizer_config.json template, including an explicit thinking-mode choice;
do not treat the README's illustrative cached tokenizer revision as our pin.
[Qwen3 example](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/qwen3/README.md).

The recipe sets KV cache and SDPA cache, fp32 graph dtype, dynamic 8-bit
activations/4-bit weights, 8-bit embedding, XNNPACK extended ops, and export
sequence/context limits **2048/2048**. Actual quantized coverage, numerical
error, allocation and usable context require export/reference/device checks.
These settings do not mean every tensor uses four bits. No universal
GPU/NPU, private inference, arbitrary training or Qwen operator coverage follows.
[Pinned YAML](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/qwen3/config/qwen3_xnnpack_q8da4w.yaml).

Upstream configuration rejects torchao low-bit kernels combined with XNNPACK;
they are alternative kernel paths. Vulkan/QNN configuration fields alone do
not verify this model on the user's SoC. Qualcomm acceleration needs its own
SDK/backend/operator/hardware review and measurements; no vendor SDK/license
was acquired here. Start with the explicit CPU/XNNPACK recipe.
[Config validation](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/export/config/llm_config.py).

The Android source build example uses arm64-v8a/android-23 and reports testing
NDK r28c, with LLM, loader, tensor, quantized/optimized and XNNPACK components
enabled; the tokenizer runner also needs regex lookahead support. The project's
already approved NDK r27.0.12077973 is a different pin: compatibility is unproven.
Do not install another NDK or accept extra terms from this research suggestion.
[Android runner recipe](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/llama/README.md#step-4-run-benchmark-on-android-phone).

Export-environment source constraints are also pinned: install_requirements.py
names torch 2.14.0 and torchao 0.18.0 on its selected test/nightly-index path;
requirements-examples.txt names transformers 5.0.0rc1. Other dependency ranges
remain upstream ranges, so this is **not a complete resolved dependency lock**.
An isolated compatible host environment, wheel hashes and reference/export
comparison must be recorded before running model code. No automatic pickle or
trust_remote_code path is authorized.
[Installer pins](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/install_requirements.py),
[Example dependencies](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/requirements-examples.txt).

## Benchmark collector contract for the pinned C++ runner

Verified CLI flags: model_path, data_paths, tokenizer_path, prompt/prompt_file,
temperature, max_new_tokens, cpu_threads, num_bos, num_eos, warmup, ignore_eos,
method_name and optional build-gated etdump_path. Use max_new_tokens; seq_len
exists but is deprecated. **No max_seq_len flag is actually defined**, despite
the seq_len help text suggesting it. Context remains bounded by the exported
PTE. cpu_threads affects the runner only when built with ET_USE_THREADPOOL.
[Runner source](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/llama/main.cpp).

Candidate invocation, not an executed measurement:

```text
./llama_main --model_path=MODEL.pte --tokenizer_path=tokenizer.json \
  --prompt_file=SANITIZED_TEMPLATE_FIXTURE.txt --temperature=0 \
  --max_new_tokens=64 --cpu_threads=4 --num_bos=0 --num_eos=0 \
  --warmup=false --ignore_eos=false
```

Use an explicitly templated synthetic fixture only. Record effective token
counts and EOS behavior: max_new_tokens is a cap, not proof of 64 tokens.
Cold process runs and warmup=true runs are distinct cases. The runtime resets
generation statistics after warmup while preserving model-load timestamps;
warmup reports are suppressed. Avoid mixing these into cold TTFT.
[Generation/report hookup](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/text_llm_runner.cpp).

Machine-readable output is a stdout line `PyTorchObserver ` followed by JSON.
The process may print generated text around it: parse only the bounded stats
marker/object, allowlist numeric fields and never persist raw stdout, prompt
contents, generated text or arbitrary stderr. Require one unambiguous valid
record and process exit 0; missing/duplicate/malformed records are failures.
Reject invalid timing order, nonfinite numbers and zero denominators instead
of replacing unavailable values with successful zero metrics.

| Metric | Raw fields / exact interpretation |
| --- | --- |
| Load milliseconds | model_load_end_ms minus model_load_start_ms |
| TTFT milliseconds | first_token_ms minus inference_start_ms; excludes loading |
| Prefill tokens/s | prompt_tokens * 1000 / (prompt_eval_end_ms - inference_start_ms) |
| Decode tokens/s | generated_tokens * 1000 / (inference_end_ms - prompt_eval_end_ms) |
| Overall generation tokens/s | generated_tokens * 1000 / (inference_end_ms - inference_start_ms) |

Count/clock caveats from the actual runner: prefill emits the first generated
token before the decode loop. stats.generated_tokens contains only the loop's
returned count, **excluding that first token**; max_new_tokens=64 can therefore
produce generated_tokens=63 without EOS. The decode loop's EOS token is counted
before its stop check. Preserve this raw count definition; do not silently relabel
it all emitted tokens. first_token_ms is taken before first-token decoding and
callback output, so TTFT is an internal prefill/encode interval, not host-observed
first byte. time_in_ms uses Android CLOCK_REALTIME (TIME_UTC elsewhere), **not a
monotonic clock**; reject inconsistent/backwards intervals and record clock
provenance. A separate host monotonic duration measures a different boundary.
[Token count implementation](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/text_llm_runner.cpp#L243),
[Decode-loop EOS/count](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/text_token_generator.h),
[Clock implementation](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/util.h#L199).

JSON also contains model_execution_start_ms/end_ms, aggregate_sampling_time_ms,
aggregate_model_execution_time_ms and SCALING_FACTOR_UNITS_PER_SECOND=1000.
prefill_token_per_sec/decode_token_per_sec appear only for positive durations.
Optional GPU byte/peak-MB fields appear only when the backend populates them;
sentinel/unavailable values are not zero memory use. **CPU RSS is absent**:
measure it separately (for example accessible /proc/PID/status VmRSS/VmHWM),
with permission/sampling/peak limitations explicit. PSS, RSS and GPU allocation
are distinct quantities. Do not equate load+TTFT with measured full process
startup or infer cold-cache timing from a new process alone.
[Exact JSON producer/formulas](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/stats.h).

## Smallest next implementation path and explicit blockers

Owner's current target is **Samsung Galaxy A72**; exact SKU, RAM, Android/API
and accessible CPU/thermal signals must come from the permitted ADB inventory.
Honor 400 Pro is superseded as target. Start with 0.6B CPU/XNNPACK 8da4w;
1.7B is gated on the first model's measured memory. This section is a research
handoff, not an already executed provisioning or phone run.

The official v1.5.1 GitHub release asset listing contains a CMSIS pack and PDSC,
not an Android llama_main binary. The checked executorch-community HF search
for Qwen3 returned a WebGPU export, not a matching CPU/XNNPACK artifact.
No reviewed immutable pre-exported CPU PTE plus matching runner was established
by this search. Unrelated community artifacts are not an automatic fallback.
[Release assets](https://github.com/pytorch/executorch/releases/tag/v1.5.1),
[Official community query](https://huggingface.co/api/models?author=executorch-community&search=Qwen3&limit=100).

**Critical loader finding:** the advertised Qwen recipe calls
export_llama_lib.export_llama, which automatically downloads/converts an HF
checkpoint if base.checkpoint is absent. Its Qwen converter writes a torch.save
intermediate, and Llama2Model later uses torch.load. The newer
extension/llm/export/load.py can read safetensors, but is not automatically wired
into this legacy Qwen recipe. Do not execute the unmodified recipe under this
repository's no-automatic-model-pickle rule.
[Actual exporter branch](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/llama/export_llama_lib.py#L702),
[Qwen converter](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/qwen3/convert_weights.py),
[Model loader](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/examples/models/llama/model.py),
[Separate safetensors reader](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/export/load.py).

Proposed bounded repair for independent review, **not implemented here**:
in an isolated checkout at the pinned commit, make the Qwen3-0.6B loader accept
only an explicitly provided local .safetensors checkpoint; load via
safetensors.torch.load_file and apply the pinned qwen_3_tune_to_meta mapping
in memory. Require base.checkpoint so HF automatic conversion cannot run.
Reject PyTorch/pickle inputs, adapters and prequantized/SpinQuant/QAT branches;
retain missing/unexpected-weight validation. Tests must demonstrate
torch.load/torch.save and network access are never reached, tied-embedding
mapping is correct, and exported results match the reference. Pin the patch
hash separately: an adapted exporter is not the untouched upstream recipe.

Concrete next steps for the integration owner:

1. Create an isolated Python3.12 environment. Use the manifest's exact
   ExecuTorch1.5.1, torch2.14.0, torchao0.18.0 and transformers5.0.0rc1 package
   candidates; resolve all transitives into a reviewed hash lock before install.
   PyPI metadata confirms Windows cp312 ExecuTorch/torch wheels and universal
   torchao/Transformers wheels; this is availability, not compatibility proof.
2. Checkout ExecuTorch at the pinned commit with recorded submodule revisions.
   Review the safetensors-only repair above before model loading. Download only
   the approved 0.6B immutable safetensors snapshot in the implementation step,
   record weight hashes and reject unlisted files. This research did not fetch it.
3. Compare pinned Transformers reference with adapted eager/export outputs on
   synthetic fixed fixtures. Use the exact XNNPACK YAML/params hashes and
   explicit context2048, capture quantization and operator/delegate placement.
   Hash the resulting PTE, external data files, tokenizer and exporter manifest.
4. Cross-build the matching arm64 llama_main from the same adapted source,
   recording CMake flags, NDK/compiler/submodule versions and binary hash.
   Check existing r27 compatibility explicitly; upstream's tested r28c does not
   authorize an implicit NDK upgrade. Deploy only after successful build checks.
5. Use the collector with sanitized templated fixture, effective token counts,
   distinct cold/warm cases, process memory provenance and thermal/cooldown
   observations. Runtime delegate evidence remains required: requested XNNPACK
   flags, export graph partitioning and a successful process alone do not prove
   every operation ran through XNNPACK. Correlate runtime profiling/ETDump with
   export/ETRecord operator maps; report portable CPU fallback separately.

Official platform guidance supports Windows with VS2022+ and **Clang-CL**,
or WSL using its Linux toolchain. Existing MSVC/Rust/JDK does not prove Clang-CL,
CMake/Ninja, export operators or Android runner prerequisites are installed.
The upstream Android example is a shell/CMake workflow; Linux/WSL is a pragmatic
candidate if native Windows dependency/build checks fail, never claimed as
already available. Current source ownership does not include provisioning or
the proposed adapter implementation.
[Versioned source-build guidance](https://docs.pytorch.org/executorch/1.5/runtime-build-and-cross-compilation.html).

## Existing operator and memory constraints

Use Qwen3-0.6B for quick diagnostics, Qwen3-1.7B as a candidate for more useful mobile inference; these are pinned baselines, NOT claims to be latest/best. Resolve exact HF revisions and hashes before downloads; no automatic main-based update. Read each model's license separately. Transformers/PyTorch reference vs ExecuTorch export must be compared for output quality/numeric error.

Verified Qwen3-0.6B config: hidden_size=1024, intermediate_size=3072, layers=28, attention_heads=16, kv_heads=8, head_dim=128, activation=silu. Use head_dim directly; hidden_size/head count is not a substitute. The revision-bound snapshot above supersedes the earlier unpinned main inspection.

Research candidates: linear projections first; attention/KV state and normalization/SiLU/softmax separately. Model masking/rotation is not automatically private. Any local mask correction must be included in cost, including repeated multiplication as costly as original. Keep tokenizer/output handling local in first experiment without claiming hidden activations are safe.

Memory inventory must distinguish weights, quantization metadata, activations, KV cache, backend buffers, OS and training optimizer states. 10 GB device RAM is not 10 GB guaranteed app budget. Full-parameter training, adapter training and inference have different budgets. Measure supported accelerators instead of selecting size solely on RAM.
