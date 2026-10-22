# Department development and evidence workflow

This is the common contract for bounded department work under
[AGENTS.md](../../AGENTS.md) and [CI review gates](ci-review.md).
It defines local execution and handoff; it does not launch agents, schedule
background jobs, authorize merges, or establish product capability.
Profile definitions in `config/check-profiles.json` are the executable check
inventory. A profile existing in that inventory is not evidence that it passed.

## Start and ownership

1. Select a brief from [the work queue](../../work/INDEX.md). Record a WORK ID,
   run ID, acceptance criteria, relevant REQ/RFC/ADR IDs and baseline commit.
2. Assign one journal owner, an integration owner and file/module owners.
   Give each bounded product change its own branch and worktree. Record branch,
   absolute worktree path, dependencies and owned paths before parallel edits.
   A shared checkout is acceptable only for explicitly disjoint file ownership;
   coordinate shared contracts through one owner.
3. Read the selected role and applicable architecture/contracts. A department
   proposes shared-core API changes before consumers implement against them.
   The core owner coordinates versioned commands, states, errors and events
   across Rust, UniFFI and Kotlin. UI fixtures must be sanitized and visibly
   distinguished from measured node state.
4. Inspect the actual toolchains. Record executable paths and versions; do not
   install or upgrade dependencies silently. Use [BUILD.md](../../BUILD.md)
   for build prerequisites and platform limits.

Parallel agents write distinct handoffs using the
[department template](../../templates/department-handoff.md). Only the journal
owner consolidates material events, failures and completion serially. Role
documents describe responsibilities; they do not prove that an agent is running.

Every agent also maintains its own MD journal. The [mandatory meeting contract](agent-meetings.md)
requires reading peers and at least 5 concrete questions after at most 3
iterations. Actual replies and decision owners are recorded; unanswered shared
decisions remain open while independent work continues. Read [project memory](../../agents/MEMORY.md)
on start/resume and link applied lessons from handoffs. This remains mandatory
when a department switches WORK or run IDs.

## Local entry point

Run from the repository root, selecting only profiles applicable to the patch:

```text
python tools/run_checks.py --profile docs --work-id WORK-0009 --run-id RUN-EXAMPLE --bundle
python tools/run_checks.py --profile workflow --work-id WORK-0009 --run-id RUN-EXAMPLE
python tools/run_checks.py --profile rust --work-id WORK-0001 --run-id RUN-EXAMPLE --bundle
python tools/run_checks.py --profile android --work-id WORK-0007 --run-id RUN-EXAMPLE --bundle
```

On Windows, use an explicit installed Python executable when the `python` alias
does not run. Python 3.12.0 was located in the current Windows environment;
the WindowsApps alias did not work. Python 3.11 or later is required.
Android commands also require the
supported shell and configured SDK/NDK/JDK; a Windows Python executable alone
does not provide an Android build environment.

The default output directory is
`.artifacts/checks/<WORK>/<RUN>/<profile>`. Use a new run ID for a new observation;
`--output-dir PATH` selects a different output location. The runner refuses to
overwrite an existing output directory; choose a new run ID for a rerun.
Keep generated evidence
outside source paths. Attach the generated report and its actual outcome to the
handoff, including the invocation exit code. A missing executable, backend or
device is unavailable or failed evidence, never a passing check.

## Department matrix

The implemented inventory supplies documentation/workflow checks and commands
for the existing Rust and Android scaffold. The remaining gates below are
required work-specific checks to implement, not claims of existing test coverage.

| Department | Local profiles / available purpose | Additional acceptance before its capability is claimed |
| --- | --- | --- |
| Transaction core | `docs`, `rust`, `storage-local` for WORK-0010 diagnostic metadata; full `storage` gate explicitly unavailable | Local ledger tests cover migrations, state/event atomicity, competing writers and process-exit rollback. Filesystem plus model DB activation still requires its own tested recovery protocol; final independent WORK-0010 review remains pending. |
| Android UI | `docs`, `android`: lintDebug, JVM unit test task, existing Android build script and declared APK output | Verify navigation, lifecycle, error/empty/loading states and actual bridge results. Separate emulator evidence from physical-device evidence; `device` is unavailable until implemented. Follow WORK-0007 scope and dependencies. |
| Protocol / sessions | `docs`, `rust`; `interop` explicitly unavailable | WORK-0004 version compatibility, independent test peer, authentication, malformed input, idempotence and reconnect/recovery cases; security review. Local ACID does not establish distributed atomicity. |
| ML / privacy | `docs`, relevant host build profile; `privacy` explicitly unavailable | WORK-0002/0003 pinned model/toolchain inventory and measured primitive feasibility, threat-model evidence, local approved privacy registry, backend denial paths and qualified privacy review. No privacy pass from transport encryption or simulated peers alone. |
| Integration | `docs`, `workflow`, relevant producer profiles | Re-run on the combined source revision, verify Rust/UniFFI/Kotlin contract compatibility and actual end-to-end paths. Track unavailable `storage`, `interop`, `device` and `privacy` gates as blockers for claims that depend on them. WORK-0008 retains release scope. |

`docs` invokes the package validator. It checks documentation/package structure,
not application behavior. `workflow` runs the repository's `tests/test_*.py`
suite, including check-runner behavior. `rust` runs
format, Clippy, tests and the desktop build; those tests cover only what exists
in the source. An Android JVM test task can succeed without relevant tests;
record actual coverage rather than inferring UI correctness from its exit code.

## Evidence and packaging

The report records commands, exit codes, environment, source revision and dirty
state. For uncommitted work, explicitly say so and identify the reviewed snapshot
with file hashes or an equivalent reproducible snapshot reference; a HEAD hash
alone does not identify modified source. Capture evidence from a stable checkout
without concurrent source mutation. A report or snapshot hash identifies source;
it does not supply independent review.

`--bundle` creates a package only after the profile passes, containing
`report.json`, explicitly configured build outputs and a SHA-256 manifest.
Failure or unavailability produces a report without a bundle. Consumers verify
the manifest and report outcome before using an artifact. A passed bundle is
not a release certificate. Artifact SHA-256 hashes cover exact file bytes;
the source inventory's `utf8-lf-v1` mode canonicalizes UTF-8 text line endings
for cross-platform source validation only. Do not apply that normalization to
binary artifacts. Do not broadly collect the workspace, runtime logs or credentials.
Use sanitized fixtures; exclude prompts, tensors, gradients, keys, tokens and
identifiable training data from evidence.

The runner does not provision toolchains/SDKs, publish or sign packages. Rust
commands use `rustup run 1.88.0` without `--install`; Android first checks that
installed toolchain. Build tools can still restore locked dependencies and the
pinned Gradle wrapper distribution over the network. This is not an offline
build guarantee; pre-provision caches when network access is unavailable.
Preserve the colleague's
Android/Termux versioning, APK archive and release rules when that branch is
integrated; consult [BUILD.md](../../BUILD.md) and that branch's release documents.
This common evidence contract does not replace those packaging policies.

## Handoff, integration and release gates

### Mandatory sprint closure: commit and GitHub push

Owner decision, 2026-10-22: every successful sprint closure must include a commit
and push to the appropriate GitHub development branch, without asking again.
The integration owner coordinates one closure; individual departments push their
own assigned branches and never include another contributor's unrelated work.

1. Read the WORK brief, inspect current branch, upstream, diff and worktree.
   Use the assigned department/integration branch; create a development branch
   when needed. Preserve collaborators' commits and local changes.
2. Finish applicable checks and independent/security review for the intended
   scope. Log observed results, unresolved capability gates and source identity.
   Review the final commit; metadata-only follow-ups need scoped rechecking.
3. Commit intended source, contracts and MD evidence. Exclude secrets, toolchain
   caches and ignored binaries. Push to the intended origin development branch
   (`git push -u origin <branch>` for its first push, then the verified upstream).
4. Verify with `git ls-remote --heads origin refs/heads/<branch>` that the remote
   SHA equals the intended local commit. Record branch, commit, push exit code,
   remote SHA/check outcome and remaining blockers in the journal/handoff.
5. Report closure only after successful push and remote verification. On auth,
   network, rejected/non-fast-forward or protection errors, keep closure pending,
   record the concrete error, preserve local commits and resolve safely. Never
   force-push or overwrite peer work to manufacture success.

This standing authorization covers development-source synchronization, with no
automatic default-branch merge or release. A bounded sprint can close while
explicitly deferred device/privacy capabilities remain incomplete; it cannot
claim their acceptance. The check runner does not execute this Git procedure;
the responsible agent must perform and log it.

The department hands over acceptance-to-evidence links, source identity, changed
paths/contracts, exact commands and outcomes, artifact hashes, blockers and the
next owner. The integration owner checks dependency readiness and contract
compatibility before combining changes, then runs applicable checks against the
combined revision. Passing checks on separate branches do not pass integration.
Department branches target the agreed integration base; they need not all target
the colleague's Termux branch. Branch protection and required CI checks must be
configured separately before they can enforce these gates remotely.

An independent reviewer other than the author and pair partner reviews the exact
latest commit. If work is uncommitted, review may identify the source snapshot,
but commit-bound acceptance stays pending until a commit exists and is reviewed.
New changes invalidate affected results. Protocol/data/privacy/crypto changes
also need security review. Record findings and their resolution in the work item.

Local success permits an evidence-backed handoff, not release. Integration needs
the applicable combined checks and independent review. Release additionally
needs the WORK-0008 acceptance evidence and configured repository authority;
critical release/privacy decisions require qualified human review. Missing
hardware, credentials or backend proof remains an explicit blocker. No automatic
merge, release or always-on project automation is enabled by this document.
