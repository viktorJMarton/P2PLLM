# WORK-0014 journal

## Run run-20261023-android-diagnostic-01

Owner requests user-visible activity after installing initial status-only APK.
Inspected existing bridge/core/CLI/SQLite and Kotlin lifecycle. Runtime owner
sqlite-layer explicitly agreed typed object run/list API and exclusive startup
recovery, bounded SQL paging and sanitized errors. Primary added bounded16-entry
registry and recorded contract before UI coding. Model agent separately resumes
WORK-0002 safe export/dependency resolution as first-priority stream.
Current changes uncommitted; implementation/review/device acceptance pending.

## UI contract acknowledgement and implementation start

Primary explicitly accepts the same v1 contract as Kotlin consumer. Additional
UI agent could not start (host agent thread limit), so primary owns both Kotlin
files while runtime/model agents keep their separate paths. No invented agent.
Implemented local diagnostic card on overview/jobs, real start/loading/result,
bounded history paging, app-private DB path and off-main native calls. Pending
ID survives savedInstanceState; screen teardown finishes native transaction and
releases wrapper without triggering recovery. VersionCode2/versionName0.2.0.
Kotlin compilation awaits generated bindings from the actual completed bridge.

## Observed compilation and review repair

Root cargo test --workspace --offline compiled but3 bridge ownership expectations
failed on Windows contention error mapping; runtimeowner fixed rawfs2 contention
comparison and reports28entries+Clippy pass. Initialfailed result not discarded.
HostDLLbuilt; UniFFI fullmetadata initially failed on uncached Android libc;
--metadata-no-deps actualDLLgeneration succeeded, binding normalized toUTF8LF.
Pinnedlibc fetched using Cargo.lock and targetAndroid, no versionupgrade.
KotlincompileDebugKotlin exit0 in1m30s. Reviewer then found RecoveryRequired retry
loop; typedprocessrestart/settings guidance +disableStart and terminalpendingID
clear added. Scopedrecompile exit0 in28s. NativeAPKbuild launched, pending.

## Actual native build and phone result

NativeARM64/RustSQLite47.54s +Gradle22s completedexit0. ExactAPK0.2.0/code2 hash
in evidence.md. Owner reconnectedA72; install-r succeeded. ActualUIbutton tap
createdSucceeded/v2/3events, visibleterminalresult, completeprocessforce-stop/
relaunch preservedsameDBrecords/events andvisibleFeladatokhistory. Earlier
2records preserved; testadded1. Currentphoneproof is separate from earlier
helperproof and hostkill tests. InitialUIAutomation screenstate failure fixed
bywake/compresseddump. No Androidactivekill/rotationinflight claimed.
PrimaryUIhandoff documents implementation/observations/remaining scope.

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
