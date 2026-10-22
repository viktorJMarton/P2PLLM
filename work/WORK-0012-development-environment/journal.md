# WORK-0012 journal

## run-20261022-environment-01

Owner: primary agent. User explicitly requested a suitable scalable developer
environment after Java absence stopped Android compilation. Started before
environment source implementation. WORK-0010/0011 source remains in progress.

- Rust1.88 is now installed and Rust product tests pass. Java17 was not
  provisioned; recording its absence without resolving it was insufficient.
- Official Adoptium API returned HTTP403; Google SDK metadata downloaded.
  Exact SDK packages and license text were identified before installation.
- SDK license acceptance must follow GOVERNANCE.md owner-legal-choice rule;
  prepare concrete pinned environment and readable license before asking.
  No SDK license accepted or SDK code executed yet.

### Provisioning and actual build

- Owner explicitly approved the listed four SDK development packages through
  the scoped license question. That supersedes the pending state above; no
  unrelated terms accepted. Archive versions/SHA256 are locked in config.
- Installed JDK17.0.20.1, SDK35r2, Build Tools35.0.0, command-line16.0,
  NDK27.0.12077973, Rust1.88 AndroidARM64 target and cargo-ndk3.5.4.
  dev_env install/doctor/check/run use a versioned shared-cache override and
  child-only environment variables, without global PATH rewriting.
- Kotlin compile passed in3m28s. Native release ARM64 bridge build passed in
  2m08s; Gradle assembleDebug passed in1m51s. Device/native-call execution remains
  unobserved; build evidence is not a release or privacy claim.
- Reviewer found a clean-JDK layout mismatch hidden by manual installation;
  fixed both layouts and added a fresh ZIP-to-activation regression. Reviewer
  also required exact version tokens: fixed near-version acceptance and added
  full-SDK-fixture regression. Six bootstrap tests now pass; reviewer rechecked.
- Bootstrap doctor passed actual required tools/files. Final combined profile,
  commit and push checkpoint follow under the user's explicit push request.
