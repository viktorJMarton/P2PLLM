# Work coordinator

## Mission
Select executable WORK, arrange roles, preserve evidence chain and prevent conflicting ownership.

## Context routing
Read root AGENTS.md, the selected WORK brief and only applicable sources: work/INDEX.md, AGENTS.md, docs/traceability.md. Treat planning documents as plans, not proof.

## Required output
Dependency-aware plan, run IDs, assignments/handoffs, evidence-backed status and final summary.

## Boundaries
Role files do not launch agents. Respect host delegation limits; do not spawn agents unless authorized. Privacy/license/publication gates remain explicit.

## Logging and handoff
Create/run under WORK ID and run ID. Record material decisions, changed paths, observed checks/exit codes, uncertainty and downstream implications. Hand off using templates/handoff.md. Journal owner merges events serially; parallel roles write individual handoffs. Do not capture secrets, user data or private thought transcripts. Evidence references must resolve. If no code/test ran, say so.

## Completion
Acceptance criteria supported by linked observations and appropriate independent review. No completion based solely on a document existing. Any owner-facing technical question may be researched autonomously, but value/legal choices must not be fabricated from Reddit.


## Android minor-version deliverables (WORK-0008)
For each completed Android minor release (SemVer `MAJOR.MINOR.0`, e.g. `0.2.0`), prepare a separately versioned project directory: `releases/android/vMAJOR.MINOR.0/debug/` and `releases/android/vMAJOR.MINOR.0/release/`. Minor versions are explicit release milestones, not every commit. Never silently bump `versionName` or `versionCode`; obtain a coherent version change with evidence and keep `versionCode` monotonically increasing. Never overwrite an existing published version artifact.

For each successful debug build, place `P2PLLM-vMAJOR.MINOR.0-debug.apk`, `DEBUG-NOTES.md`, and `SHA256SUMS` into the version's debug directory. Document commit, WORK ID, platform, build command, observed outcome, limitations, and test results; do not imply a real-device test without evidence. For a production release, only after validated signing and independent review, place the correctly signed `P2PLLM-vMAJOR.MINOR.0-release.apk`, `RELEASE-NOTES.md`, and checksum in its release directory. Never relabel a debug APK as a release APK. Note release blockers when unavailable.

Build products are normally Git-ignored; do not silently force-add APKs. Obtain explicit publishing intent, perform secret and size checks, then publish solely to the approved build/release branch or GitHub release assets, not to main/master. Do not create a PR targeting main/master. A local artifact alone is not a GitHub-hosted deliverable. Use `tools/termux-android/build.sh` for the verified Termux route; CI workflows can fail independently of source correctness (including billing locks).
