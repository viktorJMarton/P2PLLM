# Android local operator shell handoff

- work_id: WORK-0011
- run_id: run-20261022-ui-01
- department / role: Android implementation
- journal_owner: primary agent
- integration_owner / recipient: primary agent
- status: in_progress; source implemented, Android execution and review pending
- branch / absolute worktree path: work/local-storage-android-shell; C:/Users/Viktor/repos/P2PLLM
- baseline_revision: 341be683d1da785fac2d9ad0e2b75b22e396f2ca
- source_revision: uncommitted
- dirty_state: shared checkout, explicitly disjoint Android ownership
- owned_paths: android/app/src/main/java/org/p2pai/app/MainActivity.kt;
  android/app/src/main/java/org/p2pai/app/OperatorShell.kt; this handoff
- shared_contract_owner: primary agent; existing BridgeStatus contract unchanged

## Inputs and scope

[Brief](brief.md), REQ-005/REQ-009, PRODUCT.md, TECHNOLOGY.md,
agents/android.md, docs/architecture/interfaces.md,
docs/architecture/overview.md and docs/operations/department-workflow.md.
This is a local UI slice; it does not complete WORK-0007 network/contribution
lifecycle, implement inference, or supply privacy proof.

## Changes and decisions

- Five Hungarian product destinations using existing Material3/Compose only;
  no dependency, Gradle, generated binding, permission or Termux changes.
- Selected destination saved via rememberSaveable, restoring on configuration
  recreation/process recreation when Android restores saved instance state.
- Existing nodeStatus() runs on an Activity-owned single-thread executor once
  on creation and once per explicit refresh. Recomposition never calls native
  code. Concurrent refresh requests are rejected while loading.
- Loading, native-library unavailable, bounded failure and ready states are
  explicit. LinkageError and RuntimeException are caught only around the bridge
  read/projection; raw native errors are neither displayed nor logged.
- Results update Compose state on the main thread. onDestroy shuts down the
  executor and removes queued callbacks; late delivery checks destroyed before
  touching UI state. Native work cannot be forcibly interrupted; no background
  node capability is claimed by this lifecycle wrapper.
- Ready state displays actual bridge values and explicitly discloses that the
  current bridge returns NodeStatus::default(), not live task measurements.
- Navigation is horizontally scrollable with selected tab semantics; content
  scrolls vertically, safe drawing insets are applied, controls are >=48dp.
- Unsupported AI/network/model/resource controls are disabled with nearby
  explanations. No invented metrics, fixtures, active policies, runtime toggles,
  advertising or affiliate text.

## Acceptance evidence

Environment: Windows PowerShell, shared repository checkout. Plain git initially
refused repository ownership; commands below use scoped safe.directory without
changing global configuration. java and kotlinc were not found through
Get-Command in this agent environment. Primary agent owns the Android profile
attempt and broader toolchain inspection.

| Criterion | Exact command / inspection | Exit / outcome | Reference |
| --- | --- | --- | --- |
| Patch whitespace | `git -c safe.directory=C:/Users/Viktor/repos/P2PLLM diff --check -- android/app/src/main/java/org/p2pai/app` | 0 | Existing tracked MainActivity diff; untracked new file inspected separately |
| Source identity | `Get-FileHash android/app/src/main/java/org/p2pai/app/*.kt -Algorithm SHA256` | 0 | SHA-256 below |
| Contract usage | Read crates/android-bridge/src/lib.rs and generated Kotlin fields | Source inspection only | Existing fields preserved; no bridge change |
| UI compilation/lint | Android profile delegated to integration owner | Not observed by this agent | SDK/JDK/toolchain evidence required |
| Navigation/lifecycle/device | Manual verification checklist below | Not executed | Android emulator/device absent from this agent run |

Initial frozen source SHA-256 (exact bytes; future edits invalidate these):

- MainActivity.kt: 395302C6EDF0DB75E7F26AFF0528BB9E3783BA20DF3C2E61569D16F2B101BE8E
- OperatorShell.kt: 58C4D9544388CB643155EFC1F87C214A7133E55A14803DD493AE5E4C96F427DD

## Manual developer verification still required

1. On a supported Android debug build, enter all five destinations, including
   horizontally scrolling navigation on a narrow screen. Repeat with large
   system font scaling and TalkBack; verify selected tab and reachable controls.
2. Rotate on each destination and while status is loading; selection restores,
   the recreated Activity requests fresh status, and old Activity results never
   overwrite its state. Navigate away/destroy during loading and check leaks.
3. With the native library installed, verify schema/network/private capability
   labels match nodeStatus(), including the current unavailable private flags.
   Refresh repeatedly; only one call is in flight and unrelated recomposition
   does not trigger new bridge calls.
4. With the library unavailable in a deliberate developer build, verify the
   unavailable state, unknown status wording and retry action without a crash.
   Exercise RuntimeException through a developer-only test harness when one
   exists; verify bounded failure text without raw diagnostics.
5. Confirm every unsupported action is disabled, explanation remains visible,
   and there is no model/prompt input or apparent policy mutation.

## Package provenance

No APK, signed/release artifact, bundle or publication produced by this agent.
No automated UI harness exists in the inspected app source; no mirroring UI
tests were added. Successful documentation checks alone cannot verify this UI.

## Independent review

product_review notified after initial source freeze. Review and commit-bound
acceptance pending; primary agent consolidates review findings and any revised
source hashes. This author cannot be the sole reviewer. No security/privacy
mechanism is added or authorized by the UI; privacy release gates remain open.

## Integration and next action

Primary owner: run applicable docs/android profiles on combined stable source,
record unavailable tools as blockers, resolve independent review findings, then
commit and obtain latest-commit review. Preserve colleague-owned build policy.
Only the journal owner consolidates this handoff into the journal.
