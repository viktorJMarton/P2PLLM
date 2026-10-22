# ADR-011 — Durable agent personas, memory and bounded journal meetings

Status: accepted owner decision, 2026-10-22. Supplements ADR-007.
Work: WORK-0013. Requirements: REQ-009.

Each agent declares the professional persona of its primary role and owns its
own append-only MD journal. No more than3 development iterations may elapse
between documented peer-journal meetings. Every meeting contains at least5
substantive questions, affected WORK/contract, respondent, actual response and
next-action/decision status. Counters continue across runs/WORKs/branches.

Peers read each other's journals, answer in their own journal, and continue
from those observed responses. Immutable-prefix receipts allow asynchronous
append-only updates without waiting for every journal to stop changing. Missing
answers hold dependent decisions, not all departments. The coordinator may
reassign an unavailable respondent; time alone never creates approval.

Root instructions, role personas, briefs, handoff templates, durable project
memory and automated structural checks reinforce this rule. Semantic review is
still necessary: no checker can prove unlogged work did not happen or that an
agent understood a document. Persona is not a credential or a way to self-review.

Routine reversible work within accepted contracts is autonomous. Legal owner
choices, external publication scope, independent source/security review and
qualified release/privacy decisions retain their existing authority. Historical
logs remain historical; no past meeting or approval is invented retroactively.

Canonical procedure: [agent meetings](../operations/agent-meetings.md).
