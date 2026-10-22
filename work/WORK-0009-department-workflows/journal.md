# WORK-0009 journal

## run-20261022-workflow-01

Owner: primary agent. Started before implementation. User authorized automatic
project work after discussing uniform department testing and packaging.

- Base: work/WORK-0001-bootstrap, 3dc5d2b; pre-existing modification is the
  owner's WORK-0001 assessment journal. Do not revert it.
- Connected GitHub comparison still reports Termux branch 11 ahead / 0 behind.
  No remote mutation or source synchronization performed; colleague's files
  remain outside this task's ownership.
- Found working Python 3.12.0 at the explicit Python312 installation path;
  the WindowsApps alias had failed in the earlier assessment. Rust 1.88.0,
  Android SDK/NDK and physical-device verification remain unavailable here.
- Parallel work will use disjoint file ownership in this shared checkout;
  no shared journal/manifest writes by delegated agents. This bounded tooling
  change does not touch product modules or colleague-owned Android tooling.

### Implementation and intermediate observations

- Created local branch work/WORK-0009-workflows without altering the colleague's
  branch. Delegated disjoint runner/tests and workflow-documentation files;
  independent_review owns a separate review report. Owner alone updates logs,
  shared profiles and source manifests.
- Added common Python profiles, CI invocation and a department handoff template.
  Storage, independent interop, device and privacy profiles are unavailable,
  never passing substitutes for future product acceptance.
- Initial package validation returned exit 1, 295 checks: raw source hashes
  differed after Windows checkout line-ending conversion and the manifest was
  stale. Added shared source inventory with explicit utf8-lf-v1 hashing and
  portable slash paths; built artifact hashes remain exact-byte SHA-256.
  Validator/updater now use explicit UTF-8.
- Intermediate unittest run: exit 0, 18 tests, one skipped due Windows symlink
  privilege 1314. Junction rejection passed. This is superseded by final tests
  after process cleanup/source snapshot changes.
- Independent review reproduced child processes surviving timeout. Runner author
  is adding process-tree lifetime handling; taskkill failed under this sandbox,
  prompting a Windows Job Object implementation. No timeout reliability claim
  is accepted before the regression test passes.
- Rust profiles now use rustup run 1.88.0 without --install; Android checks that
  toolchain first. Clarified that build tools can restore locked dependencies
  and pinned Gradle distributions: no offline-build guarantee or SDK provision.

### Review and frozen-source verification

- Independent review resolved timeout/provisioning findings; 20 tests yielded
  19 passes and one ordinary-symlink privilege skip. Windows junction and child
  lifetime regression checks passed. Reviewer also verified .bat invocation in
  a spaced path. This is a trusted check harness, not a hostile-process sandbox.
- First real-root probes exposed Windows safe.directory formatting; fixed the
  provenance command to use a slash path. New reports identify base HEAD and
  uncommitted state correctly.
- local-workflow-001 test subprocess passed but the complete profile failed
  because the review report changed concurrently. This is expected fail-closed
  source-stability behavior. After all source writers stopped, local-workflow-002
  passed with a bundle; local-unavailable-002 returned 2 without a bundle.
- Rust profile returned 1 without downloading Rust: 1.88.0 is not installed;
  later steps were not_run. This is a named environment blocker, not Rust
  implementation validation. Detailed command/results are in evidence.md.
- Preparing source manifest, final docs check and local implementation commit.
  No push, remote CI claim, merge, APK publication or product capability change.
