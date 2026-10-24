# WORK-0015 - Usable offline Android question and answer

Status: in_progress
Run: run-20261024-local-inference-01
Owner: primary; persona Accountable delivery coordinator.
Requirements: REQ-001, REQ-005, REQ-009. Depends on WORK-0002 observed A72 inference.

Deliver one local question and bounded answer in the Android AI tab, with
preparing/running/completed/cancelled/error states. No network or saved chat.
Use the exact measured Qwen3-0.6B PTE and tokenizer, bundled for this debug
vertical slice so the APK works without a separate download. Show installation
progress; later independent model distribution is outside this change.

## Frozen department contract

Kotlin package org.p2pai.app. Native adapter object LocalInferenceNative exposes:
`external fun generate(modelPath: String, tokenizerPath: String, prompt: String, requestId: Long): String`
and `external fun cancel(requestId: Long)`. Library name p2p_inference. Generate is blocking and
must run on a dedicated worker; exactly one generation process-wide. It accepts
raw user text up to1024 UTF-8 bytes, no embedded NUL or chat control markers;
native code constructs the pinned non-thinking Qwen template and limits output
to128 new tokens/16384 UTF-8 bytes, temperature0, no prompt echo,4CPU threads.
No prompt/response/tensor logging or stdout stats. Static exceptions only:
INPUT_INVALID, BUSY, MODEL_LOAD_FAILED, GENERATION_FAILED, CANCELLED.
Cancel is idempotent and publishes a positive monotonic process request ID; the native cancelled-ID watermark covers pre-entry/load races. Older cancelled IDs cannot stop newer requests. Cancel returns quickly; terminal completion waits the current native load/prefill step. Both native and Android owners explicitly accepted this contract revision.
No Activity-owned native handle, no new work after cancellation until completion.

UI/controller loads only bundled model.pte468633472bytes SHA256
07786b553d9661d36431426d06c268f385d453314f6722ca79f66c7e79653b48 and tokenizer.json
11422654bytes SHA256aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4.
Asset prefix local-model/. Copy bounded files off main thread to app-private
storage, verify both hashes before native load, never trust existence alone.
An interrupted/invalid copy must be recoverable, not marked ready. No DB/model
activation transaction in this slice; existing Rust diagnostic storage unchanged.
Retain worker/state across Activity recreation, stop generation on background,
discard chat on process death. No prompt in savedInstanceState or logcat.

## Ownership and verification

Native department owns native/executorch-adapter/ and
tools/prepare_android_inference.py plus its targeted tests. Android department
owns Kotlin UI/controller, manifest/build.gradle settings/version0.3.0/code3.
Root owns public synthetic answer checks, work journal, packaging/device/Drive
delivery and integration. Shared contract changes require actual peer response.
Separate journals/handoffs; mandatory3-iteration/5-question meetings preserved.

Required: native build, host meaningful boundary checks, Android compile/lint/APK,
actual A72 question/answer, cancellation, Activity recreation and restart smoke.
Verify pinned bytes and no network permission. Model-quality checks are bounded
observations, not full numerical equivalence. Backend placement/privacy gates
remain open. Independent security/latest-commit review before development push.
New APK goes to the owner's versioned Drive structure with commit/hash/results.

Measured framing decision (meeting34, actual native/Android agreements): append literal ` /no_think` to validated raw text before im_end, preserving the closed assistant thinking prefix. Controlled comparison001 supports this pinned-model choice; strict answer test and full quality gates remain unchanged.

Routine reversible development is autonomous. Follow [agent meetings](../../docs/operations/agent-meetings.md): at most3 iterations, at least5 concrete questions, actual peer reads and responses; no invented approvals.
