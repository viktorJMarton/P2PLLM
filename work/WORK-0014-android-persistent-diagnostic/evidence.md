# WORK-0014 evidence

Run run-20261023-android-diagnostic-01. No implementation verification yet.
Latest ADBprobe .artifacts/phone-benchmark/device-probe-20261023-001/report.json
is blocked: no single authorized device currently observed. Earlier A72 inventory
and helper tests are historical WORK-0002 evidence, not this UI acceptance.

## Host and Kotlin observations

Windows11/Rust1.88/JDK17/SDK35. Rootinitial cargo test --workspace --offline:
exit1, bridge6pass3fail contentionclassification. Runtimeowner fixed fs2rawerror
and reports28entries pass plus Clippy; handoff-runtime.md contains exact scope.
RoothostDLLbuild exit0. Kotlinbinding generated from actualDLL with
uniffi-bindgen --metadata-no-deps (allUniFFItypes in workspace); initial full
metadata lacked cached libc0.2.191. Target lockedfetch succeeded.

`python tools/dev_env.py run -- <absolute android/gradlew.bat> -p android
--no-daemon :app:compileDebugKotlin`: exit0/1m30s. AfterreviewUI recovery-guidance
fix, same scoped command exit0/28s. These compile records are uncommitted source
observations, not native-library load or user-action/device acceptance. Final
frozen common profiles/commit review remain to be recorded.

## First full native APK build

`python tools/dev_env.py android-build` exit0: ARM64 release Rust/SQLite/fs2
build47.54s, GradleassembleDebug22s/35tasks. DebugAPK11277843bytes, SHA256
f1d5de1f3d526361bdd807deaf6436af8953844697831bcc3fe86d77dd44d913.
ZIP native entries onlyarm64-v8a Rustbridge/JNA/androidxgraphics. Version0.2.0,
versionCode2. This is packaging evidence for uncommitted source; no device/UI
execution or full phone benchmark inferred. Final profile/artifact supersedes
this first artifact if any source change affects packaging.

## Actual A72 user action and process restart

Run ui-smoke-001,2026-10-23, currentSM-A725F/Android14/API34/5625888KiBRAM.
adbinstall-r succeeded for exactAPK above, coldstartok. ActualownappUI button
tap produced1newSucceeded record/version2 and3events; visible success verified.
OwnappDB inspected in-memory only; no rawDB/personal data stored. Then
amforce-stop org.p2pai.app andfreshamstart: same terminal/version/events preserved,
savedhistory visible onFeladatok. Existing2records preserved, observed3aftertest.
Report .artifacts/device/WORK-0014/ui-smoke-001/report.json passed=true.
InitialUIAdump failed untilscreenwake; compresseddump corrected, XMLremoved.
USBpowered/battery28.8C/thermalstatus0 finalprobe; no modelworkload.
UncoveredAndroidcases: activeRunningprocesskill/rotationduringactivework.
Host deterministicOSkill separately covers recoverylogic. No AI/privacy/release
acceptance follows from the bounded successfuldiagnostic/device observations.

## Final validation and compatibility repair, 2026-10-23

Common runner on Windows11/Python3.12/Rust1.88/JDK17/SDK35, source uncommitted:
- final-001/docs passed (661 checks plus agent policy); workflow exit0,
  65 tests:64 passed,1 Windows symlink privilege skip; rust exit0,
  fmt/Clippy/28 test entries (including2 child helpers)/desktop build passed.
- final-001/android failed lint NewApi: generic UniFFI Cleaner required API33
  while minSdk26. JVM/APK steps not run in that failed profile.
- Added crates/android-bridge/uniffi.toml android=true, regenerated actualDLL
  bindings with pinned UniFFI0.28.3 and explicit --config. Official Android
  template selects guarded API34 cleaner or existing JNA fallback. No lint
  suppression, minimumSDK bump or new dependency. Reviewer inspected fix and
  reported no blocker. Generation script and Android README use same config.
- final-002/docs passed662 checks plus agent policy; final-002/android exit0:
  Kotlin/lint, JVM task NO-SOURCE (no JVM test coverage), ARM64 native/APK build.
  Reports: .artifacts/checks/WORK-0014/final-001/{docs,workflow,rust,android}/report.json
  and .artifacts/checks/WORK-0014/final-002/{docs,android}/report.json.

Final APK0.2.0/code2:11319266bytes, SHA256
 d6ac4cab5dbeaafd812dfaf9a5fbbb118f8659671e7fa4f73ce5ddcd9b963e89.
It supersedes first f1d5de1f artifact. Actual install-r and own-app revalidation
on SM-A725F/Android14 passed ui-smoke-003:9prior records preserved,1new terminal
record/version2/3events, visible success; force-stop/relaunch preserved all10
records and visible history. Report .artifacts/device/WORK-0014/ui-smoke-003/report.json.
ui-smoke-002 failed a harness assertion expecting capitalized SQL state;
SQLite contract stores lowercase succeeded. Corrected only ignored harness,
retained failed report and repeated complete scenario. No product change needed.
Android active-running kill/rotation, model inference and privacy remain outside
this observation. Source commit/review, verified push and Drive delivery follow.

## Verified source checkpoint and Drive delivery, 2026-10-23

Branch work/WORK-0002-phone-baseline; source commit
05768ccbe9b9bbcb0f1c265465349e91dd3650ac. Independent product-review actually
bound exact reviewed runtime/UI/binding/config/collector/export/test hashes to
this clean commit and reported NO BLOCKER for development checkpoint/push.
No implementation or pair ownership by reviewer. WORK2 export/benchmark and
privacy acceptance remain open. Latest docs profile final-003 exit0,665checks
plus agent policy pass after journal/handoff updates; tested code unchanged.

`git push -u origin work/WORK-0002-phone-baseline` exit0. Subsequent
`git ls-remote --heads origin refs/heads/work/WORK-0002-phone-baseline` exit0,
observed remote SHA05768ccbe9b9bbcb0f1c265465349e91dd3650ac equals source commit.
Default branch untouched; no release/merge/force-push.

Google Drive skill used for authorized artifact delivery. Exact final APK
SHA256d6ac4cab5dbeaafd812dfaf9a5fbbb118f8659671e7fa4f73ce5ddcd9b963e89,
11319266bytes,0.2.0/code2,ARM64 debug, uploaded under existing owner hierarchy:
https://drive.google.com/drive/folders/178qOjlv-KAksy9sOgeQ7syvbEREkBOyv
- p2pllm_v0.2.0_code2_c05768cc_debug_arm64-v8a.apk, id1WQ_gpQYC-W2FrHEcl5D3QYt0RkEg0BA6
- BUILD-INFO.json, id1u_m06dHR_zK-F3T1Jq328ZRImNF4LxFu
- SHA256SUMS.txt, id1vHa_zFxwGqWMDjIxmGbPS-W7KwPpyznS
- TEST-RESULTS.json, id1DAvLU9HlEYgjkIfH315-UOB7bIY1laGt

Connector folder readback confirms all4 names and sizes; APKmetadata readback
confirms exact11319266byte size and correct parent. SHA is local exact uploaded
bytes; connector exposes no remote checksum, so no remote hash claim.
Buildinfo links source commit; testfile includes frozen common reports and
actualA72 ui-smoke-003 evidence plus limitations. Debug packaging is not release.
This metadata-only follow-up records already observed source push and delivery;
its own exact-commit review/push/remote verification is still pending here.

WORK14 bounded diagnostic implementation/phone persistence/delivery complete.
Uncovered activeRunning Android kill/rotation is explicitly retained; host
actualOSkill and live-reopen tests remain distinct. Next model owner continues
WORK2 guarded export, then numerical validation, exact Androidrunner/backend and
repeated onphone measurements; no user-visible AI claim follows from this APK.
