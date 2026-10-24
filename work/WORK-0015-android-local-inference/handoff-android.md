# Android department handoff

- work_id: WORK-0015
- run_id: run-20261024-local-inference-android-01
- role/persona: android / Pragmatic Android platform engineer (agents/android.md)
- recipient: primary integration owner
- status: in_progress (source delivered; compile/device/review pending)
- source_revision: uncommitted shared working tree

Implemented process-owned LocalInferenceController with one generation executor,
background cancellation executor, monotonically increasing native request IDs,
main-thread Compose state and memory-only prompt/answer. Fixed bundled files are
bounded copied into noBackupFilesDir, SHA256 verified before native load on every
run; partial files removed/rebuilt. Background Activity stop cancels; rotation
keeps process worker/state. Busy persists until worker terminal state. Error
messages are static; no chat logging, persistence, network or arbitrary paths.

AI tab now accepts bounded text, generates/stops/retries, shows preparing
percentage/running/completed/cancelled/error and visible answer. Existing Rust
diagnostics remain. Updated unavailable-feature wording; version0.3.0/code3,
allowBackup=false, generated model asset source and pte/json noCompress. No new
dependencies. JNI declarations match accepted requestId Long contract/ADR-013.

Changed paths: android/app/src/main/java/org/p2pai/app/{LocalInference.kt,
MainActivity.kt,OperatorShell.kt}; android/app/src/main/AndroidManifest.xml;
android/app/build.gradle.kts; own journal and this handoff.

Verification: scoped Git whitespace check exit0, Windows PowerShell with explicit
workdir/per-command safe.directory. Initial default-cwd Git check failed and is
recorded; no global config mutation. Root owns Kotlin compile/lint session9100,
native/asset staging, APK inspection, actual A72 question/answer, cancellation,
rotation/background/restart smoke and latest-commit independent security review.
No build or phone success is claimed here.

Follow-up: root reported Kotlin compile passed current marker validation; lint
was pending session9100. Gradle now guards package/assemble/bundle Debug+Release
with exact streaming model/tokenizer/LICENSE size+hash checks and required
inference/C++ runtime ELF64 AArch64 shared-library structural validation. Raw
packaging cannot silently ship a missing local inference payload. Guard execution
and APK identity verification remain root-owned/pending; header checks alone are
not binary provenance. Gradle scoped whitespace check passed exit0.

Journal: work/agent-journals/inference-android.md iteration2; meeting after1 read
actual primary iteration27 and native Start, later native iteration1 responses.
AND-Q1..3 actual native answers and AND-Q4..5 actual root answers are recorded.
Meeting after iteration3 adds AND-Q6..10 to native/primary/reviewer about final
stripped headers, runtime notices, actual guard execution, provenance scope and
device evidence. Responses pending; see journal for exact owners. LSN-005/006 applied to ownership/evidence; no
review approval inferred. Next responsible agent: primary for integration and
required checks; Android agent available for compile/device findings.

Closure: no commit/push performed by department; root retains integration owner
responsibility for review, commit, development-branch push and remote SHA proof.

Iteration4 follow-up: added testAPK-only platform runner
org.p2pai.app.LocalInferenceSmokeInstrumentation, configured testInstrumentationRunner.
Normal five-check mode exercises production controller/native + real Activity;
`-e mode restart` asserts empty process state then real answer after root force-stop.
Checks preparing/running cancellation, duplicate/retry rejection, preparing/running
Activity recreation, real moveTaskToBack background stop and foreground retry.
Sanitized result Bundle only;120s phase deadlines. No new dependencies. Also guard
requires exact nonempty runtime-notices/inventory.json and executorch/LICENSE.
Native confirmed17-component inventory staged (not legal certification). Root owns
testAPK compile and actual device execution. Whitespace check passed exit0.

Iteration5 repair: root build85926 found Gradle `java` extension shadowed fully
qualified java.security.MessageDigest. Explicit import now resolves it; scoped
whitespace check passed exit0. Root reruns build; no new result claimed.

Iteration6: root build57607 main/testAPK/lint passed but omitted guard task;
fixed Task Spec lambda to explicit it.name. Earlier bare name silently matched
project name. Own dry-run blocked by inaccessible WindowsApps python alias exit1;
root runs graph plus controlled missing-model negative packaging test and restore,
then positive build. Scoped diff check passed. Meeting6 recorded before further
iteration; AND-Q11..15 actual verification/review questions open with named peers.

Iteration7: root reports Android profile offline-app-001 passed/stable and actual
guard negative/positive cases passed. Root released only test source to add real
visible AI tab interaction through platform UiAutomation (set text/click generate/
assert visible exact2), then existing lifecycle checks. No new dependency or main
APK source changed. Testfile SHA2566214328b3601c0e304deca437ef11fa0b2f5e018091c3528694d41985803227c;
whitespace check exit0. TestAPK compile/lintAndroidTest/actual UI execution pending
root. No raw accessibility tree/text/prompts/answers logged or serialized.

Iteration8 test compile46531 failed on show-on-screen constant owner. Corrected
exactly three refs to AccessibilityAction.ACTION_SHOW_ON_SCREEN.id. Testfile now
SHA2562d98da892db49ec75fac5efc6e2130b282c878043825ade744894cd19af5d578;
diff check exit0. Frozen for root targeted compile/device rerun; no pass claimed.

Iteration9: actual root smoke003 payload/manifest/install pass and boundedcanary
pass, but visible question production COMPLETED failed strict2 check, zero cases
accepted. Added public-fixture-only failure diagnostics bytes/SHA/standalone2/
protocol/thought/exactExpected/closed terminalPhase, no rawtext. Strict2 unchanged.
Testfile SHA256d27d2ab5b4135b956c643663b688f51cb83406487eae93d72e6162bb0b944dfd;
diff check exit0. Meeting9 recorded before next iteration; root controlled CLI
comparison and targeted testAPK diagnostics pending. No app acceptance claimed.

Administrative policy repair: canonical WORK-0015 question cells and explicit
actual-read prefix receipts added to own journal. Original full historical read
hashes/questions/answers/dates/counters preserved; surviving1025-byte native Start
prefix receipt is explicitly limited because native later question formatting
changed historical bytes. Own journal validation passed exit0/issues=[]; other
journals remain their owners' scope. No source/APK changes; metadata refrozen.

Quality-meeting follow-up / run quality-meeting-android-20261024-01: owner reported
poor answer quality; Android source inspection found full accepted input/output
Strings preserved, but >1024UTF8B edit is rejected wholesale (old text remains),
128new-token termination has no exposed stop reason, and generation is singleturn
without history/system/HU instruction. No concrete owner payload examined; these
limits are not a diagnosed cause. Existing6+2smoke repeat one short arithmetic
fixture and do not establish Hungarian/general quality. Own journal iteration10/
meeting10 contains7concrete questions, actual root/reviewer answers and remaining
native/root respondents. Proposed unchanged-pin/template12publicHUfixture
reference/CLI/app comparison with input/output identity plus score/stop metrics;
synthetic only, no personal chat or hashes. No product code/model changes or new
benchmark performed. Root owns qualitypilot brief; next Android step is measured
public-fixture transfer/UI plan after agreed rubric and contracts.

Meeting10 closed with actual native/root/reviewer responses to all7questions.
Native confirms unknown stopreason and singleturn; root agrees unchanged baseline
pilot plus separate history scope. Candidate gate >=10/12correctness2,0critical,
0unexplained deterministic ref-device/app loss is measurement selection only,
not HU product acceptance. Root synthesis/docs/review/push next; no new APK,
model change or benchmark executed by Android. Own metadata now frozen.
