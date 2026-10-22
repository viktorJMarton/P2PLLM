# Work traceability and IDE querying

Chain: owner request -> REQ -> WORK -> RFC/ADR -> agent journal/peer meeting ->
role run/handoff -> files/commit -> test evidence -> review -> outcome. Persistent
project memory lives in MD, not an assumed agent's recollection. No private
chain-of-thought capture; store concise rationale, alternatives and observations.

Read work/INDEX.md then selected brief/journal/evidence. Journals contain material decisions, failures, corrections and next steps. events.jsonl is append-only observed events, not predicted success. One owner writes the journal; parallel roles write distinct handoff files. Generated indexes are disposable; sources remain Markdown/JSONL/Git.

Every agent also owns a separate MD journal. After at most 3 iterations, read the
other agents' journals and document a meeting with at least 5 substantive
questions, respondents and actual answer/decision references. See the
[meeting contract](operations/agent-meetings.md), [journal template](../templates/agent-journal.md)
and [project memory](../agents/MEMORY.md). Work journal ownership and per-agent
journal ownership are distinct; the coordinator consolidates serially.

Sample IDE request: Explain why WORK-0003 chose this privacy primitive, cite the ADR, math assumptions, failed trials, implementation commit and latest reviewer findings. If an artifact does not exist, explicitly say unknown.

Development logs are not node runtime logs. Runtime retention is bounded/local and excludes prompts, tensors and user data. Test artifacts include safe fixtures, command, exit status, environment and sanitized output; link long output rather than duplicating it.
