# Offline Android inference evidence

Run: run-20261024-local-inference-01. Windows11/Python3.12.0, pinned JDK/SDK/NDK.
Branch work/WORK-0015-offline-android-ai; source initially uncommitted on9f33493.
[Portable actual results](device-observations.json) include receipt hashes,
exact APK/device identity and sanitized instrumentation results.

## Observed working slice

Debug version0.3.0/code3, ARM64. APK509885353bytes, SHA256
f91a77d23774228a48b3f827fce536297b3d3bae3aba843e9118270091ee6a19.
On Samsung SM-A725F/Android14/API34, actual accessibility interaction selected
the AI tab, entered a public arithmetic fixture, clicked Generate and observed
the exact expected answer in the visible UI. No response text is logged.

Normal instrumentation passed6 checks with resultcode-1: visible question/answer;
preparation cancel/retry rejection; preparation Activity recreation/answer and
duplicate rejection; native-running-phase recreation/cancel; background cancel;
foreground retry/answer. A real force-stop preceded a separate restart run:
empty in-memory state and a new answer passed2 checks/resultcode-1. This tests
Activity.recreate, not a physical sensor rotation. Native cancellation may wait
for a load/prefill step; this is not an immediate-interrupt latency guarantee.

Merged APK manifest has no INTERNET permission and allowBackup=false. Streaming
APK audit matched model/tokenizer hashes, all18 notice-component inventories,
and packaged JNI bytes. Bounded app-UID logcat canary found none of the public
prompt/protocol/tensor needles in its last1000 lines since test start; raw logs
were discarded. This establishes tested-path evidence, not universal native
confidentiality or a peer-computation privacy guarantee.

## Reproducible checks and binary identity

`tools/dev_env.py check --profile android --work-id WORK-0015 --run-id offline-app-002`
passed all4 subprocess checks with stable source fingerprint: toolchain, lint,
JVM task (no JVM tests), and common native/Rust/APK preparation/build. Platform
test APK was actually compiled and installed; it uses no added test dependency.
Workflow profile offline-final-001 passed81 tests:80pass/1Windows symlink privilege
skip. Native host boundary/golden-template/EOS tests and6 staging tests passed,
also independently checked in their applicable revisions.

The packaging guard was tested negatively: removing the known model asset made
assemble fail at verifyLocalInferencePayload; finally restored the file. The
positive common build then executed the same guard successfully. Initial Gradle
MessageDigest shadowing and task-Spec receiver bugs are retained in journals.

Native08 source library8446904bytes SHA256
31f07120532a34495c671e4b40c05aef7bf1843d1307fe1a9adcecc44caa2901.
Approved NDK llvm-strip --strip-unneeded reproducibly produces the exact APK
library8446896bytes SHA256
f4792a7486d85c0802a11bc3c6db990b174a7e75eff3bd34bc8f7f7974984038.
Keep these distinct identities: AGP transforms the source library. Fresh PAL/
stdout binding receipts apply to native08; source and packaged byte hashes are
bound by strip-provenance-002, not an unexplained hash waiver.

## Failures preserved and acceptance limits

Smoke001 stopped before install at pre-strip-versus-packaged hash mismatch.
Smoke002 passed payload audit but stopped at a host manifest-parser boolean
format mismatch. Smoke003 installed/executed but failed strict answer formatting.
Controlled same-pin/A72 comparison001 supported adding the Qwen /no_think suffix;
the strict assertion was retained. Smoke004 passed after rebuilding. No model
export/pin/quantization was changed and no failed receipt was overwritten.

This is one bounded offline question/answer demo. Full reference/export numerical
equivalence, broad answer quality, actual backend-placement acceptance, sustained
thermal/resource policy, peers and private computation/learning remain open.
Questions/answers stay in process memory; no durable chat or model updater is
implemented. Bundled model distribution makes the APK approximately510MB and
requires additional private-storage space on first use. Only the observed A72
runtime is accepted here; Windows preparation does not verify other build hosts.

Independent latest-commit review, source push/remote SHA and versioned Drive
delivery are recorded in the journal/handoff when actually performed.
