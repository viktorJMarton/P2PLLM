# Native department handoff

- WORK-0015; run-20261024-native-inference-01.
- Agent / journal owner: /root/inference_native.
- Role/persona: android / Pragmatic Android platform engineer.
- Integration owner: primary/root.
- Worktree: C:/Users/Viktor/repos/P2PLLM; shared branch work/WORK-0002-phone-baseline.
- Baseline9f33493; source uncommitted. No independent commit/push by department.
- Owned paths: native/executorch-adapter/, tools/prepare_android_inference.py,
  tests/test_prepare_android_inference.py, own journal and this handoff.

Implemented actual ARM64 JNI blocking generation with approved requestId
extension, strict Unicode/input limits, process-wide single owner and atomic
pre-entry cancellation watermark. Worker-only runner.stop avoids load/pointer
races; load/prefill finishes before cancellation completion. Pinned non-thinking
Qwen template, temperature0/4threads/128newtokens,16384UTF8byte output cap;
recognized split EOS markers consumed, unknown protocol markers fail closed.
No prompt echo; upstream warming flag suppresses token/report stdout; strong PAL
and library-local printf/fprintf/puts/putchar wrappers discard known output paths.
Remaining vfprintf/fputs imports mean this is not universal native confidentiality.

Preparation never exports or runs a model. It verifies exact pinned PTE/tokenizer/
Qwen license, source/submodule revision, existing approved static runtime/NDK;
builds official runner-linked libp2p_inference.so and stages generated assets plus
JNI/C++ runtime files. Exact paths including partials and nested CMake output use
safe_path.18pinned component notices with component/source provenance and byte
hashes stage under local-model/runtime-notices; provenance is no legal certificate.

Observed checks on Windows11/Python3.12, VS CMake3.28/MSVC19.39 and NDK27.0.12077973:

| Check | Outcome / evidence |
| --- | --- |
| Actual JNI ARM64 compile+staging | exit0 `.artifacts/checks/native-inference-05/report.json` |
| Native Unicode/cancel/busy/EOS host executable | MSVC Release compile+execution exit0, `.artifacts/native/adapter-host-tests/Release/boundary_test.exe` |
| `python -m unittest tests.test_prepare_android_inference -v` |6/6passed exit0; junction redirects and repeat notices tested, no skips |
| Actual final binary PAL/wrapper symbols/disassembly | exit0 `.artifacts/checks/native-inference-05/output-bindings.json` |
| Actual notice deterministic twice-stage | exit0 `.artifacts/checks/native-inference-05/runtime-notices.json` |
| Scoped `git diff --check` | exit0 |

Library8446744bytes SHA256
2dbfa35eb928788a9e570c5127090b224f3a1db5af58c0cfb3f82e2c3b8b6037.
Notice inventory SHA256eaf02495a4fd59985b54c1f954ac08f30e2f317e62572836cd6287e13090bb0f.
Outputs android/app/src/main/jniLibs/arm64-v8a and
android/app/build/generated/localModelAssets/local-model.
Rebuild: `.artifacts/venvs/qwen-export/Scripts/python.exe tools/prepare_android_inference.py --output .artifacts/checks/UNIQUE --jobs 2`.
Requires execution permission for approved NDK tools in this environment.

Initial failures preserved: MSVC UTF8 flag, sandbox compiler denial, CMake imported
scope, first notice exclusive-write, shell test quoting. No failed attempt relabeled
as success. No actual model/phone run by native department. Root owns real app
answer/cancel/lifecycle/restart/logging canary and packaging receipts. Independent
reviewer reran earlier5tests/host binary and accepted path/EOS source, pending
final notice-delta and exact-commit review. Root must commit/review/push/verify
existing development branch before successful sprint closure; closure pending.

Journal [inference-native](../agent-journals/inference-native.md): iteration7,
meetings3and6; five questions each, actual peer responses recorded, all answered.
NAT-Q10 Android confirms cancellation wins terminal state despite native load
failure; both owners preserve current binary for this controller slice. Next
owner root; no active native writers.

Update iteration8: root/native/Android explicitly accepted measured literal
` /no_think` user suffix before im_end after root meeting34. Exact full-template
golden host test passed exit0; actual JNI build/stage run08 passed exit0.
Latest source library8446904bytes SHA256
31f07120532a34495c671e4b40c05aef7bf1843d1307fe1a9adcecc44caa2901;
this supersedes run05 library above. Evidence
`.artifacts/checks/native-inference-08/{report,output-bindings}.json`.
Notice inventory hash unchanged. No general quality claim: root must rerun
unchanged strict app assertions and lifecycle/restart against rebuilt APK.
Root must retain source versus AGP-strip-transformed APK library hashes with
explicit pinned-tool transformation receipt; no same-byte claim. Journal now8,
meeting next by9/before10. Source frozen; no API/controller/model pin changes.

Owner quality feedback checkpoint: native iteration9/meeting9, six concrete
questions and actual cross-department replies in own journal. Owner reports
answers are unsatisfactory; bounded arithmetic/lifecycle pass does not resolve
this. Read-only investigation found no float/token-ID/quantized-reference versus
PTE quality parity evidence, no EOS-versus-budget result, single-turn/no history,
and128newtoken cap. Current0.6B/8da4w capacity or export loss causes are unproven.
Recommend root-owned preregistered12public Hungarian useful-task pilot with exact
template/token-ID/config checks then same-pin reference/CLI/app comparison;
English pairs optional diagnostic controls. No new export/model or product-code
change by native department. Larger model is evaluation candidate, no promised
improvement/shipping. Meeting questions remain open until actual peer responses;
counter9/lastmeeting9, next by12/before13. Next owner primary for bounded sprint.

Meeting9 now has all6actual responses: root accepts12HU pilot plus separate G01
greeting-loop blocking regression, reference-first model decision and test-only
budget A/B; Android confirms single-turn/missing stopreason; reviewer accepts
token parity then float/PTE then quantized-reference attribution, frozen template.
Sanitized owner G01 symptom is repetition/partial directive-like fragment; no raw
personal response saved. A fragment is no proof of quantization/export/template
cause. Next actual work: unchanged current A72 CLI/app G01 reproduction, then
same-pin reference, no tuning or output concealment. All product code still read-only.
