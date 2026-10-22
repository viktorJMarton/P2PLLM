# Agent journal meetings and autonomous continuation

Status: mandatory owner decision, effective 2026-10-22; WORK-0013.
This is the canonical meeting procedure under [AGENTS.md](../../AGENTS.md).

## Cadence and journals

Every agent writes its own `work/agent-journals/<agent-id>.md`, using
[the journal template](../../templates/agent-journal.md). The agent's iteration
counter continues across WORKs/runs/branches. One bounded implementation,
analysis or repair plus its verification/result is an iteration; failure counts.
Do not count every shell call, hide multiple independent changes in one cycle,
or restart the counter to evade synchronization.

Declare one primary [professional persona](../../agents/PERSONAS.md) in the
journal and handoff. Apply the selected role's decision/evidence/communication
style; role changes are explicit and never reset counters or review independence.
Meeting response bookkeeping itself is not another development iteration;
a substantive new analysis, implementation or verification cycle is.

After no more than **3 iterations**, before the next iteration, each agent:

1. Appends its actual result, changed paths, command/outcome, blockers and next
   intention to its own journal. Record source commit or uncommitted snapshot.
2. Reads the other agents' latest journals, including unresolved questions.
   Record peer path, canonical source hash/revision, iteration and read time.
   A content hash alone is not proof that an agent understood a peer entry.
3. Writes at least **5 concrete questions** about those logged changes. Each has
   an ID, relevant WORK/contract, responsible respondent, impact, proposed next
   action and status: open / answered / decided / blocked.
4. Posts its answers to received questions in its own journal, citing the
   question ID and evidence. It may notify a running peer, but the MD entry is
   the durable record. Only the owner of a journal appends to it.
5. Re-reads the responses and records any actual shared decision with both
   participant references. An author cannot fabricate peer agreement or use a
   meeting as independent PR/security/privacy approval.

This is asynchronous coordination; it need not be a simultaneous chat. Each
agent must read its addressed questions before the next dependent work. A
meeting may close with open questions only if the next independent work and
blocked shared work are explicitly separated. It does not close those questions.

## Questions and decision authority

Questions must concern a real journal change, test failure, shared API, conflict,
assumption or dependency. Five cosmetic rephrasings do not satisfy the minimum.
Avoid busywork for obvious reversible fixes: state the proposed/default routine
action, let the responsible peer validate it, and keep unrelated work moving.

The contract owner decides routine technical details within accepted ADRs.
Cross-contract changes require the affected owners' recorded responses and
relevant ADR/RFC/tests. Independent review still applies to the final revision.
Privacy/release decisions requiring qualified review and actual owner legal or
publication choices retain their existing authority; a peer cannot waive them.

If an agent is unavailable, record last observed handoff/journal and the reason.
Ask the coordinator to reassign the respondent or preserve the question as
blocked. Never claim a two-party decision from one available agent. Historical
handoffs may supply context, but are identified as handoffs, not newly attended
meetings. Continue only work independent of the unresolved decision. Do not
repeat identical permission questions or stop all departments for one blocker.

## Persistent learning and enforcement

[agents/MEMORY.md](../../agents/MEMORY.md) records observed failure, correction,
evidence and the preventive check. It is project memory, not a claim that model
weights were trained. Read applicable lessons at start/resume and at meetings;
record which changed the current action. Proposed lessons never silently change
accepted requirements. A lesson is adopted only with evidence and clear scope.

Root instructions, every role guide, journal/handoff templates and automated
policy checks must agree on the 3-iteration/5-question rule. Missing a meeting,
question owner or response reference is an explicit workflow failure, not a
passing placeholder. Historical records before this decision are preserved and
identified as historical; do not manufacture retroactive meetings.
