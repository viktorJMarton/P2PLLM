# ADR-013 - Bounded Android local inference adapter

Status: accepted implementation direction for WORK-0015, 2026-10-24.

ADR-006 remains the shared-core direction. For this first local-only vertical
slice, Kotlin calls a narrow JNI ExecuTorch adapter directly. This explicitly
narrows the current composition boundary: no new general Rust runtime, network
authorization, diagnostic ledger or persistent AI task contract is introduced.
Future shared task scheduling must integrate this backend through the core port;
this adapter does not authorize remote execution or model installation policies.

Use the exact measured model/tokenizer/runtime revisions. Bundle the public
model in the debug APK for an immediately usable offline build; disclose the
roughly480MB payload. A pinned asset pair is copied and hash-verified in private
storage before use. No remote executable/plugin or arbitrary model selection.
Distribution outside the APK and activation/rollback remain separate work.

One process-owned worker survives Activity recreation. Generation has bounded
input/output/context, explicit busy/error/cancel states and positive monotonic
request IDs. A cancelled-ID watermark closes cancellation before JNI entry;
native load/prefill may finish before cancellation becomes terminal. The worker
owns the runner; cancellation does not access an initializing native pointer.
No UI-thread hashing, inference, prompt logging, saved chat or network permission.

WORK-0002 numerical equivalence, full backend placement and sustained thermal
gates stay open. Bounded public answer checks and an actual installed-app smoke
test are required for this slice; a successful build alone does not pass them.
Independent security review covers storage recovery, Unicode boundaries,
cancellation and suppression of upstream payload logging.
