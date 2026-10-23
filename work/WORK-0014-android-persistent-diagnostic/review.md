# WORK-0014 independent runtime/UI review

Reviewer /root/product_review, primary persona pr-review with secondary security
lens; neither runtime nor UI implementation coauthored. Run
RUN-20261023-DIAGNOSTIC-REVIEW-01. Initial source is uncommitted on
work/WORK-0002-phone-baseline; final commit binding pending.

## Findings

No blocking correctness/security finding in reviewed Rust runtime source.
Strong process registry preserves exclusive ownership across Activity wrapper
recreation; startup recovery occurs only before exposing a newly acquired owner.
try_lock contention returns Busy and never runs recovery on a live handle.
Shared storage lease removes duplicate ownership policy; pinned fs2 raw
contention mapping handles observed Windows differences. SQLite closes before
lease drop. Parameterized SQL reads at most51 rows to return50; offset10000 is
an explicit traversal bound, not total count/completeness guarantee.

**Medium UI finding, open:** MainActivity.runDiagnostic catches typed
RecoveryRequired as generic Exception and recommends refresh/retry. If finish
fails after Running commits, the same runtime deliberately never recovers live
owners; pending ID remains and each retry returns RecoveryRequired until process
restart. Show an explicit truthful recovery instruction rather than suggesting
ordinary retry repairs it. Do not add Activity recovery or interrupt a live owner.

Nonblocking UI follow-up: after rotation, successful refresh can observe a
terminal saved pending ID without clearing it; the next start action merely
returns that old result. Clearing pending ID once its terminal record is observed
avoids ambiguity while retaining idempotence for unknown/active outcomes.

UI source inspection otherwise shows off-main native/file calls, saved pending
ID, native completion rather than teardown cancellation, sanitized errors and
actual persisted-result return. A successful run remains displayed if subsequent
history listing fails; no in-memory success fallback exists. Diagnostics are
explicitly labelled local checks, unavailable AI/network remain disabled.
Generated API matches inspected Rust record/page/object methods by source;
native library/Kotlin compatibility still needs the actual build.

## Observed verification

Read WORK brief/contract, shared core tasks, storage lease/pagination, CLI reuse,
bridge runtime/tests, MainActivity/OperatorShell, actual generated Kotlin binding
and app versionCode2/versionName0.2.0. Inspected implementer handoff that records
initial Windows contention failures, subsequent28 tests and Clippy success;
these are implementer-run observations, not independent build evidence.

Reviewer directly ran already-built
`target/debug/deps/p2p_android_bridge-a0debedd484d60cc.exe --test-threads=1`:
exit0,9 entries pass, including one child helper that is a no-op without its
child-only environment. Tests exercise real OS child kill after Running commit,
same exported registry reopen while live, external lease exclusion, once-only
recovery, bounded pages, stable errors and stored idempotent result/event count.
Reviewer did not independently rebuild this binary; final frozen profile must
establish exact source/build identity. No Android runtime/device check performed
by reviewer; historical WORK-0002 helper tests are not this UI evidence.

## Initial exact-byte source SHA-256

| Path | SHA-256 |
| --- | --- |
| crates/android-bridge/src/diagnostics.rs | 040E053F2FA0BDF0103F3E2670FFF0DAACE7B4D243D9C9FDBB8FF929C0DF9456 |
| crates/node-core/src/tasks.rs | D3512F1EDC6D0CB66C71F95A5B05AF6CAFA8D1E0FEAD5470914DBE407ED737D0 |
| crates/storage-sqlite/src/lease.rs | 2CEC112E9A9F68872B0FAD3A2E0E4A93DF6115B5881D9AC8F51121B697C4ADD0 |
| crates/storage-sqlite/src/lib.rs | 4A27EDA2EF8F6559F9C974684F8A4AF9861098BC67A8D74D245172BED2F6ABA8 |
| crates/node-cli/src/diagnostics.rs | 505BE643FA3559C170458353ABF7D3DCD6A9DE367CA30DDD346FCA8CC5EB31B2 |
| android/app/src/main/java/org/p2pai/app/MainActivity.kt | 3D316E117830DBFC7B23A27A2814FBBABB24446BA4FA62FBEA784F87D856E4D5 |
| android/app/src/main/java/org/p2pai/app/OperatorShell.kt | 6AE171B94F642E9294F66468FC4E1A773CF4C7C3E66A7556F7F69F4CB618CB25 |
| android/app/src/main/java/uniffi/p2p_android_bridge/p2p_android_bridge.kt | 4476594FE18B70F84429E16E5EEA40524BD421129AF4C015F5D4FDB0EC9A64C5 |

Next: scoped UI error correction/recheck, real native/Kotlin APK validation,
exact-commit review. Missing device remains an explicit acceptance blocker;
no AI/privacy/full storage/model-activation or release acceptance follows.

## UI fix and real-device evidence recheck

Medium RecoveryRequired finding **resolved** in latest source: typed error gives
explicit full-process stop/restart guidance, app-settings shortcut and disables
new runs while recovery is required. No Activity recovery introduced. Terminal
pending ID is cleared only when refreshed records prove it completed; record/page
schema version1 is checked. No blocking remaining source finding in this slice.

Latest UI exact-byte SHA256:
MainActivity.kt 03D41C62FC1DEDBD7D95B7E1B3845E1C0B165FEDFCA99D27021C832EA8882403;
OperatorShell.kt 512F4CCFE418866FA76D5DA36F9A516ED2B2A53E66A2DA9F49B4852E1E5B5A6B.

Read primary-run `.artifacts/device/WORK-0014/ui-smoke-001/report.json`:
SM-A725F Android14/API34, APK0.2.0/code2 SHA256
f1d5de1f3d526361bdd807deaf6436af8953844697831bcc3fe86d77dd44d913.
Actual button/UI result, one newly persisted Succeeded/version2 record/3events,
forced process stop/relaunch preserving records and visible saved history passed.
This supplies bounded real-device diagnostic-path evidence, not model inference
or active-Running Android crash/rotation coverage. Host deterministic OS-kill
coverage remains separate. Reviewer inspected the report, did not personally
execute device steps. Final frozen common profiles and commit binding pending.

## Android cleanup compatibility and final APK readback

First Android profile correctly failed NewApi lint: default JVM Cleaner required
API33 despite minSdk26. Scoped fix independently inspected: uniffi.toml sets
bindings.kotlin.android=true; generated pinned-UniFFI code uses SystemCleaner
only on API34+ with RequiresApi guards and existing JNA fallback below. No SDK
raise, lint suppression or new dependency. Generator/docs pass same config.

Latest exact-byte SHA256:
generated binding09973E4958B91F3C8E52C6F041D67ABB843E53EAE17A79D72F80982D5BE5A535;
uniffi.toml C6A2F9046381D4695AB877F7A6362185634538D4EC5858F6FC5DC417D30F6F10.

Read final-002/android and docs reports: stable source fingerprint
8b219a13ff123d4f58adde1c758da8133e4d47af2961f14fe1821e790611e95e,
all command exit0, docs662+policy; lint/JVM/ARM64 APK passed. JVM NO-SOURCE means
no JVM behavioral coverage. Earlier final-001 workflow/Rust passed on prior
frozen snapshot; compatibility fix changes generated Kotlin/config, not their
executable implementations. Initial lint failure is retained as history.

Final APK11319266 bytes independently SHA256 matches
d6ac4cab5dbeaafd812dfaf9a5fbbb118f8659671e7fa4f73ce5ddcd9b963e89.
Read primary-run ui-smoke-003: actual A72 update installed, new Succeeded/v2/
3events record, visible success/history and force-stop/relaunch persistence
passed (9 existing records preserved,10 after). Earlier smoke002 harness case
assertion failure was preserved and corrected in ignored harness, not product.
This supersedes prior f1d5 APK evidence; no active-running Android crash/rotation,
model inference or privacy acceptance inferred. No remaining blocking review
finding for this bounded development checkpoint. Exact commit binding pending.

## Exact committed checkpoint confirmations

Read-only inspection confirmed clean source commit
05768ccbe9b9bbcb0f1c265465349e91dd3650ac on work/WORK-0002-phone-baseline;
reviewed runtime/core/lease/SQL/CLI/UI/generated binding/config hashes matched
exactly, final APKd6ac...3e89 matched, no blocking bounded checkpoint finding.

Follow-up3810a4f8cf5e1cefaa306ddd6e9638d379946b54 was clean, only seven metadata
files including manifest changed. Git diff against05768cc for crates/tools/tests/
config/android/Cargo exited0 with no changes. Read actual closure003/docs pass;
closure001/002 failures retained. Scoped verified status and delivery readback
appropriately exclude AI/release, remote checksum and uncovered active lifecycle
claims. Both confirmations were sent to primary before its actual push, with
remote SHA verification assigned to primary. No source edited by reviewer.
