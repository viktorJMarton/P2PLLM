# Autonomous development loop v1

**Implementation:** [tools/autodev.py](../../tools/autodev.py) and [config/autodev.tasks.json](../../config/autodev.tasks.json). This is a deliberately bounded single-task coordinator, **not** a running scheduler, an actual multi-agent system or an automatic merge service.

## Invocation

From a clean Git worktree with Python 3.11+:

```bash
python3 tools/autodev.py plan
python3 -m unittest discover -s tests -p 'test_autodev.py'
python3 tools/autodev.py execute --timeout-seconds 3600
```

`plan` is read-only and prints JSON containing the selected item, ranked eligible work and blocked reasons. Exit 0 means eligible work, 2 means none, 3 means invalid input.

`execute` is **explicit**, never triggered by a documentation change. It launches exactly one bounded `codex exec` with workspace sandbox and no interactive approval requests. It does not schedule itself, create subagents, commit, push, merge, publish or approve any security profile. External policies and actual Codex CLI version may still block it; never bypass restrictions. Exit 124 denotes timeout. An unclean worktree fails closed. Review its output, diffs, tests and evidence before any follow-up.

Initial prioritization is a transparent heuristic from `config/autodev.tasks.json`:

`score = 3*impact + 2*unblocks + confidence - effort - 2*risk`

Each dimension must be an integer 1–5. Higher score wins; ties prefer in-progress then lexicographic WORK ID. Dependencies must be explicitly marked `verified` in their briefs; unknown IDs and dependency cycles reject the plan. `blocked` and `verified` items cannot run. Scores are provisional owner-editable estimates, not objective measurements.

## Development control loop

1. **Observe:** inspect `work/INDEX.md`, individual status, dependency and evidence. Never equate document presence to successful tests.
2. **Choose:** run `plan`; select one runnable bounded task. If none, report blockers.
3. **Execute:** one isolated change with run ID, strict scope, budget and no automatic privileged action.
4. **Verify:** run relevant unit/integration/build checks. Mark unavailable device/testing environments as blocked, not passed.
5. **Review:** separate implementer and reviewer where possible; security decisions require qualified independent review. Re-review latest commit.
6. **Record:** concise evidence, changed paths, commands/exit codes, decision and next step under the WORK journal/handoff. Do not fabricate agent discussions.
7. **Re-plan:** after accepted status/evidence changes. Avoid unbounded self-recursion.

## Structured decision meetings

Meetings are **artifacts that resolve a decision**, not claims that multiple agents actually convened. Proposals use `docs/operations/meeting-template.md` and must yield a decision, a bounded WORK action, acceptance check and owner/reviewer—or a justified blocker. Four types:

- Architecture Council: competing design options, trade-offs, ADR proposal and compatibility.
- Engineering Sync: build/test failure analysis, smallest unblocker, runnable next task.
- Red Team Review: attack hypotheses, negative test and privacy assumptions; never self-certify security.
- Product Steering: user value, scope, measurable acceptance and owner-only product/legal choices.

A meeting without evidence or a resulting action is marked **no decision**; its notes never count as delivery.

## Autonomy boundaries

Automatically allowed within repository task scope: local reversible edits, unit tests, documentation, diagnostic research and isolated experimental code. External publication, protected branches, releases, secret handling, data disclosure, licensing and privacy-profile approval are not delegated. An unavailable approved cryptographic backend must remain unavailable; never downgrade.

Agent delegation is conditional on host/user authorization; this script launches no agents itself. If a task needs a new technology, ADR or user choice, prepare a proposal and continue with an independent eligible task when possible.

## Metrics and next implementation phase

After each real run, calculate only from observed evidence: elapsed work time, accepted WORK tasks, blocker age, failed-check rate, review rework rate, and linked verified REQ coverage. Missing data is `unknown`, never zero/passed.

Before enabling scheduled unattended execution, add: atomic lease/lock to prevent concurrent runners, structured run output and durable journals, controlled retry budgets, a verified CI review gate, stop/resume control, executable microtask breakdown, worktree isolation, and integration tests on actual Linux/Android hosts. A cron job without these controls is not production-safe orchestration.

## v1 acceptance

- Dependency-correct deterministic selection, blocked state rejection, policy validation.
- A read-only plan command and explicit bounded one-task execution.
- No autonomous Git push/merge or security approval.
- Unit tests for selection, unknown dependencies, cycles and blocked work.
- Truthful reporting of missing execution or hardware evidence.
