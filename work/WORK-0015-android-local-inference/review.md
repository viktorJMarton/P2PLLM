# WORK-0015 independent correctness/security review

Reviewer /root/independent_review; primary persona pr-review / Independent
correctness reviewer; run REVIEW-20261024-JNI-01. Own [journal](../agent-journals/independent-review.md)
iterations3-9/actual meetings3,6,9. No implementation coauthored by reviewer.

Verdict: no blocking finding for bounded Android offline question/answer slice
at this uncommitted source snapshot; final exactcommit binding still required.
Medium host path containment and notice repeatwrite findings were fixed and
independently rechecked (targeted6/6 tests exit0, no skip). Final native host
Unicode/request gate/EOS/golden-template boundary binary independently exit0.
No broad tests, model export, device execution or raw payload-log inspection by
reviewer. Actual build/device evidence belongs root/native owners.

Kotlin process worker survives recreation, gates retries until generation and
cancel drain complete, publishes positive IDs; native watermark covers preentry
cancel without accessing initializing runner pointer. Model/tokenizer copies
use appprivate noBackup storage, bounded offmain exact hashes and recoverable
partial replacement. JNI strict UTF conversions/output bounds/static errors,
measured nonthinking template, known stdout/PAL suppression and package guards
reviewed. ADR013 explicitly records narrow direct JNI architecture exception.

Actual smoke004 receipt: main APK509885353B SHA
f91a77d23774228a48b3f827fce536297b3d3bae3aba843e9118270091ee6a19.
Independent streaming verification matches model/tokenizer/packagedSO plus
18notice components/48files. Strip002 receipt hash matches smoke004 and records
approved pinned NDK exact source31f07120...aa2901 to packagedf4792a74...984038
transform,8446896B. Source and packaged hashes remain distinct; initial failed
hash audit is not waived. Normal instrumentation6 true checks/code-1 and restart2
true checks/code-1 include visible AI question/answer, preparing/running cancel,
recreation/background/retry and fresh process empty state. Bounded UID canary
passed tested prompt/protocol/tensor needles, raw logs not saved. No universal
native logging/confidentiality guarantee: vfprintf/fputs imports remain; PAL/
wrapper source/disassembly and tested canary provide bounded path evidence.

Common Android offline-app002 report all4steps exit0/stable; workflow report
passed/stable. Full numerical equivalence, general quality, actual placement,
sustained thermal, privacy and release gates remain open. No new phone run by
reviewer. Test-only public diagnostics do not authorize hashing personal chat.
Outstanding metadata questions: retain failed attempts and document current
Windows-specific common-wrapper preparation; root next responsible owner.

## Reviewed raw source hashes

```json
{
  "native/executorch-adapter/inference.cpp": "176005f9b747b51d9ec37a581d7a5d79a203520e2f789facf5e0b780b9d4afa3",
  "native/executorch-adapter/boundary.h": "68b9abf5051f523e49807c3be01b58542771130f510be0f80c8c60221dee6b5e",
  "native/executorch-adapter/boundary_test.cpp": "1bf4710a7abd3d98f7eb063b22480fff3a404dde9aa199f61eac2940a7c280a0",
  "native/executorch-adapter/CMakeLists.txt": "8097eb5321703eaad283c0091134315adafd57902a39fb338e740a99ce1fbef4",
  "tools/prepare_android_inference.py": "09afa01ed1e691a9f6c77caaa9de6e173ec5254ff246752ecea4f9a028045862",
  "tests/test_prepare_android_inference.py": "626198448caaece9eeac9497b3e0e31799d70a2d289ba4acd433a71338e3f6b8",
  "tools/build_android.py": "a768dd965a7c19baf12e26740e82674e05f5a3e8241499101eb1ee888205bd5a",
  "android/app/build.gradle.kts": "b6b9eaf6987f3fc2bf3effe196b13ac6829025a8c263a818bb7df65b0b7094e5",
  "android/app/src/main/AndroidManifest.xml": "3b4d25f9790f654f2a7a728c32544adb14a2e2af866469715e00d35e402e6a08",
  "android/app/src/main/java/org/p2pai/app/LocalInference.kt": "fdeeeb748ba29c026dddf73c8464862ba2178dbfc66f0b7e4f2ecf1ed5647217",
  "android/app/src/main/java/org/p2pai/app/MainActivity.kt": "1f2db515f2a2ddb459741ad0a1dd61484a02738feb454691c2a0e49d56dddaea",
  "android/app/src/main/java/org/p2pai/app/OperatorShell.kt": "73f846c7dc5df0ec91ec3427cf8e6e6bca324c628e2c36cf64485b0b49cc6525",
  "android/app/src/androidTest/java/org/p2pai/app/LocalInferenceSmokeInstrumentation.kt": "d27d2ab5b4135b956c643663b688f51cb83406487eae93d72e6162bb0b944dfd"
}
```
