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

## Mandatory sprint closure and GitHub push (owner decision, 2026-10-22)
Every successful sprint closure includes committing its intended source/docs and
pushing to the appropriate existing GitHub development branch. This standing
owner authorization does not require repeated confirmation. Follow
docs/operations/department-workflow.md: inspect branch and diff, pass applicable
checks, obtain required review, commit, push, and verify the remote branch SHA.
Record branch, commit, push outcome and remote verification in the work log and
handoff. A local commit alone is not a closed sprint; a failed push leaves
closure pending with the actual blocker. Preserve other contributors' changes;
never force-push, merge into the default branch, or publish a release under this
authorization. Sprint closure does not complete capabilities with missing gates.

## Department workflow
Use docs/operations/department-workflow.md and config/check-profiles.json for
common local/CI checks and bounded evidence packaging. Run applicable profiles
through tools/run_checks.py; use templates/department-handoff.md for parallel
department handoffs. Unavailable profiles are blockers for their capabilities,
not waived checks. Evidence packaging never authorizes merge or publication.

## Mandatory agent journal meetings (owner decision, 2026-10-22)
Every agent declares one primary professional persona from agents/PERSONAS.md
and the selected role's Persona section. Record it in its own journal and
handoff; apply that role's evidence, decision and communication style. A persona
change never resets meeting counters or grants independent reviewer status to
an implementer. Persona is not a claim of human credentials or agent execution.

Every working agent owns a separate Markdown journal. After at most **3
development iterations**, before starting iteration 4, refresh that journal,
read the other agents' journals, and record an asynchronous meeting. A bounded
change plus its verification is one iteration; failures count. Tool calls alone
are not iterations. Do not reset the counter by changing WORK, branch or run.

Each meeting must contain at least **5 concrete questions** about the logged
changes, with question owner, affected WORK/contract, answer/decision status and
next action. Record which peer journal revision was read. Shared decisions need
actual peer responses; silence, elapsed time and unavailable agents are not
consent. Continue independent reversible work while shared decisions remain open.
Never invent a meeting, peer answer or approval. See
docs/operations/agent-meetings.md and templates/agent-journal.md.

Routine implementation, tests, dependency setup and recovery within accepted
scope proceed autonomously. Escalate only actual owner decisions or missing
authorization, with evidence and a recommended concrete resolution. Handoff
must identify outstanding peer questions and the next responsible agent. Before
resuming, read applicable entries in agents/MEMORY.md and apply their checks.
