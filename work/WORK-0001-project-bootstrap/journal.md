# WORK-0001 journal

## run-20261017-2217z — bootstrap implementation

Owner: orchestrator. Roles read: architecture, Android, desktop-node, testing.
The Android implementation has a separate role handoff; the owner maintains this
journal. The initial handoff was validated before product files changed.

- Selected WORK-0001 because it has no dependencies (work/INDEX.md). Applied
  ADR-003, ADR-006 and ADR-007. Scope: local status and an unavailable remote
  privacy capability; no model or network operation was implemented.
- Imported 109 Drive files, 146463 bytes. The original package validator
  passed 257 checks before development. Created Git `main` and staged the
  original package plus .gitignore. The owner supplied Git identity, and the
  initial snapshot was committed as `68ef58f` on `main`; work continues on
  `work/WORK-0001-bootstrap`.
- Added Cargo workspace, shared node status, CLI status, UniFFI bridge,
  pinned Rust 1.88.0 and UniFFI 0.28.3, build recipes, and CI foundation.
  Generated a Kotlin binding from the host bridge library. Android project
  work is delegated to the Android role.
- First `cargo test --workspace` failed: Rust 1.84 lacked dependency support;
  installed pinned 1.88.0. Second attempt found an invalid `Args.as_slice()`
  call; fixed it. `cargo test --workspace --locked` then passed (2 tests).
  `cargo clippy --workspace --all-targets --locked -- -D warnings` and
  `cargo build --workspace --locked` passed. `p2p-node status` emitted local
  unavailable capability state.
- Package validation after product edits failed because the static manifest
  describes the original handoff. Updated validation to inspect Git source
  files and added a manifest refresh tool. An intermediate source snapshot
  passed 275 checks; after Android sources and build files, `just check`
  passed 286 checks before the final documentation update.
- The delegated Android role did not deliver files before it was interrupted;
  the owner completed a minimal Kotlin/Compose app, checked-in UniFFI
  binding, and Gradle wrapper. Wrapper JAR checksum matched Gradle's
  published value; Gradle 8.11.1 launched on the local JDK 17 and
  `:app:tasks --all` configured successfully. The full Android build was
  not run because the SDK/NDK is absent. Inspected the official SDK build
  tools 35.0.0 archive after checking its size and hash; `aapt2` is
  x86-64, while this host is aarch64. Further large SDK/NDK downloads
  cannot enable an official local APK build. Refreshed manifest and
  `just check` passed 286 package/source checks plus Rust formatting
  and Clippy. Resolved the Android dependency graph with Gradle and
  generated `android/app/gradle.lockfile`. Added and ran a repeatable
  UniFFI binding regeneration script, normalizing generated whitespace.
  The final source state passed 290 package/source checks and 2 Rust tests.

Open: Android SDK/NDK and physical device unavailable in this proot;
Android cross-build, device behavior, AI inference, and privacy properties are
not verified. Independent code review is pending latest diff. Next: finish
Android scaffold validation, refresh manifest, run local checks, review,
then commit.
