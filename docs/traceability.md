# Work traceability and IDE querying

Chain: owner request -> REQ -> WORK -> RFC/ADR -> role run/handoff -> files/commit -> test evidence -> review -> outcome. Use work item IDs and run IDs; roles are not persistent magical memory. No private chain-of-thought capture; store concise rationale, alternatives and observable actions.

Read work/INDEX.md then selected brief/journal/evidence. Journals contain material decisions, failures, corrections and next steps. events.jsonl is append-only observed events, not predicted success. One owner writes the journal; parallel roles write distinct handoff files. Generated indexes are disposable; sources remain Markdown/JSONL/Git.

Sample IDE request: Explain why WORK-0003 chose this privacy primitive, cite the ADR, math assumptions, failed trials, implementation commit and latest reviewer findings. If an artifact does not exist, explicitly say unknown.

Development logs are not node runtime logs. Runtime retention is bounded/local and excludes prompts, tensors and user data. Test artifacts include safe fixtures, command, exit status, environment and sanitized output; link long output rather than duplicating it.
