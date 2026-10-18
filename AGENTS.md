# Repository agent contract

## Read routing
Read PRODUCT.md and TECHNOLOGY.md for new components. Use docs/security/threat-model.md for any data flow/security work; schemas/ for contracts; docs/architecture/overview.md for boundaries. Work from work/INDEX.md and the selected brief. Load only the role under agents/ needed for the task, and relevant linked decisions. Do not reread the full repository for trivial edits.

## Truth and scope
This is a planning baseline. Never describe planned code, scheduled jobs, privacy guarantees or benchmarks as implemented. Work statuses and evidence must reflect observed results. Missing privacy proof is a blocker, not a documentation detail. Preserve accepted user decisions; technical research may recommend changes through ADRs.

## Engineering
Apply Clean Code and DRY with cohesive modules, explicit errors and minimal useful abstraction. Share contracts/business rules, not accidental duplication. Enforce local ACID with transactions and invariants; network workflows use explicit versioning, idempotence and recovery. Filesystem + DB activation needs a tested crash-recovery protocol. No arbitrary peer code, executable Python payloads, automatic model pickle loading or unreviewed dynamic plugins.

## Work and logging
Use one WORK ID per bounded change; start a run ID before work. Log material decisions, changes, verification failures, handoffs and completion in that work directory. Keep concise rationale and evidence, not private reasoning transcripts. Include file paths, RFC/ADR/REQ IDs, test command, exit code, environment and commit when available. If uncommitted, say so. A completed plan is not completed implementation.

One journal owner per work item. Parallel agents write separate handoffs; the owner consolidates serially without silently rewriting history. Prefer separate worktrees for parallel code changes. No unsupervised concurrent append to the same events file.

## Delegation and review
Delegate only when the current user's environment permits it. Role documents describe responsibilities; they do not imply agents are running. Implementer and pair partner must not be the sole PR reviewer of their own patch. Security-sensitive changes need security review. Mathematical models are assumptions-bound and checked against measurements. Critical release/privacy decisions need qualified human review; routine reversible work proceeds without repeated confirmations.

## Privacy and evidence
Peer claims are untrusted. Choose privacy profiles from a local approved registry; no remote privacy_verified flag can authorize work. Fail closed when a required backend/profile is unavailable. Do not log prompts, tensors, gradients, keys, tokens or identifiable training data. Sanitized fixtures only. Secure transport != private computation; secret sharing != safety against arbitrary collusion; aggregation != differential privacy or poisoning resistance.

## Research and changes
Official source/code/paper first; Reddit is a lead or experience report, not technical proof. Pin model revision, tokenizer, export config and dependency versions. Research deputy proposes, never silently upgrades. Update the relevant RFC/ADR and tests when a contract changes.

## Definition of done
Applicable checks pass; acceptance criteria have linked evidence; independent review applies to the latest commit; logs and contracts are current. Missing hardware, backend or credentials must be named as blockers, not bypassed.


## Android minor-version deliverables (WORK-0008)
For each completed Android minor release (SemVer `MAJOR.MINOR.0`, e.g. `0.2.0`), prepare a separately versioned project directory: `releases/android/vMAJOR.MINOR.0/debug/` and `releases/android/vMAJOR.MINOR.0/release/`. Minor versions are explicit release milestones, not every commit. Never silently bump `versionName` or `versionCode`; obtain a coherent version change with evidence and keep `versionCode` monotonically increasing. Never overwrite an existing published version artifact.

For each successful debug build, place `P2PLLM-vMAJOR.MINOR.0-debug.apk`, `DEBUG-NOTES.md`, and `SHA256SUMS` into the version's debug directory. Document commit, WORK ID, platform, build command, observed outcome, limitations, and test results; do not imply a real-device test without evidence. For a production release, only after validated signing and independent review, place the correctly signed `P2PLLM-vMAJOR.MINOR.0-release.apk`, `RELEASE-NOTES.md`, and checksum in its release directory. Never relabel a debug APK as a release APK. Note release blockers when unavailable.

Build products are normally Git-ignored; do not silently force-add APKs. Obtain explicit publishing intent, perform secret and size checks, then publish solely to the approved build/release branch or GitHub release assets, not to main/master. Do not create a PR targeting main/master. A local artifact alone is not a GitHub-hosted deliverable. Use `tools/termux-android/build.sh` for the verified Termux route; CI workflows can fail independently of source correctness (including billing locks).
