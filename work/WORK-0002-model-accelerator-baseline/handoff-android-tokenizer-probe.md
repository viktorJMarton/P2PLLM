# Android tokenizer diagnostic handoff

WORK-0002; run g01-tokenizer-probe-android-20261024-01. Persona: Pragmatic Android
platform engineer (agents/android.md). Owner inference_android; recipient primary.
Source uncommitted; no production model/JNI/core/API/APK change.

Standalone native/quality-tokenizer-probe uses existing pinned ARM64 static
libtokenizers/HFTokenizer, encode0/0. Invocation:
`quality_tokenizer_probe <verified staged tokenizer.json> <public framed prompt file>`.
Only compactJSONintegerIDs stdout, no newline; root consumes in memory and saves
hash/count, never raw IDs. Prompt1..4096B, strictUTF8/noNUL; tokenizer fixedname+
11422654B; IDs1..1024. Staticstderrerrors, known formatted/Android/syslog imports
suppressed. Tool assumes root independently verifies pinned file hashes before
staging; file size check alone is not provenance.

Actual pinned NDK configure/build passed after initial sandbox clang denial;
final suppressed-log rebuild exit0, readelf ELF64LE/AArch64PIE and import audit
exit0. Binary21901064B:
.artifacts/native/quality-tokenizer-probe-001/quality_tokenizer_probe,
SHA2567c4e8827702bc26954d525b63e1f7b083de59bffa1e1f921e1b69fc0c929df03.
No device execution by department. Root compares canonicalJSON digest against
reference20tokens/c41ba66abcf08e7419954aec698c740d0abd07ca201cffc7c0e78073ccaebaf5.
Known static-link suppression is not a general OS/native confidentiality claim.
Root owns device staging/run, exactinput/tokenizerhash binding and acceptance.

Journal inference-android.md iteration12; last actual meeting10, next by13before14.
Native answered prior referenceparity/raw-trim/stopreason questions. Actual G01
app+CLI258B samehash/repetition and float15B/7tokens divergence are recorded from
sanitized receipts; cause not proven. No modelweights/templates/criterion changed.
No commit/push by department; root retains final review, developmentbranch commit,
push and remoteSHA verification responsibility after applicable checks.

Iteration13 follow-up (separate bounded source change, same department): Gradle/
LocalInference now consume root-owned config/local-inference-model.json schema1
strict9fields via generated BuildConfig model/tokenizer bytes+SHA. Packagingguard
uses same parsedpins, Kotlin no duplicatedpins. Failclosed invalid/missing/unknown
fields; exactcurrentrevision and8da4w/int8 profiles only. OldPTE/tokenizer and
version3/0.3.0 unchanged; root owns any later verifiedcandidate transition.
No Gradle/device build by department. Standalone diff check exit0; actualgeneration,
manifest-negativecases and newPTE/device/app checks root-owned/pending. Journal
meeting13 has7concrete questions, rootQ1..3 actualanswers, active successorQ4..7
pending (oldnative/reviewer unavailable), no assumedapproval. GradleSHA276ff11c...bd2e,
KotlinSHA10336183...5907. Source uncommitted; final root integration/review/push.

Meeting13 closure: primary actually answered Q4..7 (candidate-only evidence,
unchanged JNI/no selector/privateclaim, DRY not provenance, realPTE/device/app and
latest independent review before version4delivery/push). Respondent is primary;
this does not replace pending successor independent review. All7questions have
actual answers. Root reports31targeted tests and phone20tokenparity pass; newPTE
stillpending audit. Android code/metadata frozen; no further build performed.

Iteration14: fixed embedded13publicfixture mode=pilot added to test-only runner,
androidTestassets tests/fixtures only, productionassets unchanged. Run
`am instrument -w -e mode pilot org.p2pai.app.test/org.p2pai.app.LocalInferenceSmokeInstrumentation`.
Sequential productioncontroller300s/case, validatedG01/HU01..12 corpus. Output
pilot_results_json sanitized lengths/SHA/repetition/fragments; exact/HU06strictJSON
numeric31(31.0/exponents allowed) yield deterministic_match bool, qualitative null.
ALL correctness not_human_rated; no mismatch->0 or keyword->2. passed means completed
observations, not qualityacceptance. Partialfailurearray/staticcodes; no rawtext.
No Gradle/device run/model/version/nativeAPI change by department. TestfileSHA
d72bb138aba3e34d7daadf2c58a71c2eead4ecfd40137e67865464f0e787267c;
diffcheck exit0. Root owns compile/actualA72pilot/fixture and APK identity/latest
independentcommit review. Iteration14; nextmeeting by16before17.
