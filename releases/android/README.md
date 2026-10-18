# Android release artifacts

Each approved SemVer minor release is stored under `releases/android/vMAJOR.MINOR.0/`.

```text
releases/android/v0.2.0/
  debug/
    P2PLLM-v0.2.0-debug.apk
    DEBUG-NOTES.md
    SHA256SUMS
  release/
    P2PLLM-v0.2.0-release.apk
    RELEASE-NOTES.md
    SHA256SUMS
```

Debug output is generated after a successful local or CI build by `tools/termux-android/archive-apk.py`. Source of versionName and versionCode: `android/app/build.gradle.kts`. The current bootstrap version is 0.1.0, so subsequent builds remain v0.1.0 until an intentional version bump. `--allow-existing` accepts only an identical APK; changed bits at the same version require a version/code decision, not an overwrite.

Git ignores APK files by default. Files produced locally are **not** automatically available on GitHub. GitHub Actions can upload them as downloadable run artifacts when runner billing is enabled and the job succeeds. Publishing binaries to Git or GitHub Releases is an explicit, reviewed action on an approved non-default branch. Avoid committing APK binaries into Git history unless specifically authorized; GitHub Releases is preferred for distributable binaries.

## Release gate

Release APKs must be independently signed, checked on real Android devices, and approved. Never rename a debug APK as a release APK or invent test results.

Release note template:
- Version and versionCode:
- Source commit / WORK ID:
- Added / changed / fixed:
- Compatibility and minimum Android SDK:
- Security / privacy status:
- Signed artifact provenance:
- Verified test device(s) and outcome:
- Known limitations / rollback:
- SHA-256 checksum:

Debug note template:
- Version and versionCode:
- Commit / WORK ID:
- Build and toolchain details:
- Changes in this minor version:
- Local compile result:
- On-device smoke test evidence or "not tested":
- Known issues and unavailable capabilities:
- SHA-256 checksum:
