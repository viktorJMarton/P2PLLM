# WORK-0004 journal

The first implementation activity is recorded below; full WORK-0004 acceptance
remains open.

## 2026-10-25 - First executable public loopback slice

WORK-0004 / run-20261025-protocol-loopback-01; owner primary, persona
Accountable delivery coordinator. Branch work/WORK-0015-offline-android-ai,
baseline 17703b57938e859ea4074d7d704a4c8493eb7f54. Source is currently
uncommitted. The protocol agent owns new Rust crate files and its own journal;
the testing agent owns a separate Python TCP peer and journal; primary owns
workspace membership, this work log and the handoff. The security agent owns
only its own review journal. Their meeting questions and actual answers are
recorded in those journals and primary meeting70. No concurrent shared append.

The implemented bounded slice and limits are in
[handoff-loopback-lab.md](handoff-loopback-lab.md). Rust unit tests three passed,
fmt/Clippy/build exited 0; the independently written Python peer passed 11/11
actual Windows loopback TCP cases against the rebuilt Rust binary. One
30-second byte-trickle scenario observed disconnect at about 30.11 seconds,
after a first test-helper failure due to unhandled Windows abort; both attempts
remain in the protocol agent journal. Earlier Python 8/9 and first 11-case
fixture failures were harness issues, corrected and retained in its journal.
See [evidence](evidence.md) for commands and measured limits. This paragraph
reports department observations; final combined check/source identity and
exact-commit security review are pending.

Status in_progress. RFC-0001 authenticated peer identity/session, the draft
protobuf schema, persistent replay handling across reconnect, active compute
cancellation, Android and Linux interoperability, secure private computation
and privacy-profile approval are **not** complete. No personal-derived remote
inputs are accepted by this loopback fixture. Next owner primary freezes source,
runs docs/workflow/Rust/independent-peer checks, obtains exact-commit security
review, pushes development branch and verifies remote SHA. Full WORK-0004
acceptance remains open after this bounded lab checkpoint.

## Exact-commit review correction before push

The first local source commit `359da1822b85f7b604eed7e2845c5563f20bfeb1`
was **not pushed**. Independent security review found a documentation blocker:
the crate README incorrectly promised RESOURCE_LIMIT for partial EOF/timeout,
while the Rust reader closes without a protocol response in those cases.
The reviewer reproduced partial EOF with a disposable public socket; its helper
exited 0 after receiving zero bytes. The protocol owner corrected only its
README. Primary also corrected the stale WORK-0004 no-implementation lines in
this journal/evidence and the work queue's opening status. No Rust/Python code
changed. Re-run source inventory/docs checks, amend the unpushed commit and
obtain fresh exact-commit security review before any development push. The
earlier review blocker remains part of this history, not a passing verdict.

## 2026-10-25 - Reviewed lab checkpoint and Rust client

The corrected host-lab commit `2507705fc37474d38fc3c06a1a000a6e0abfcb7f`
received independent exact-commit security review with no blocker for the
public synthetic loopback scope. It was pushed to
`work/WORK-0015-offline-android-ai`; `git ls-remote --heads origin
refs/heads/work/WORK-0015-offline-android-ai` returned that exact SHA, exit 0.
Full WORK-0004 acceptance remains open.

Follow-up WORK-0004 / `run-20261025-protocol-cli-02`, owner primary,
persona Accountable delivery coordinator, starts from that remote-verified
checkpoint. The currently uncommitted std-only `p2p-lab-client` sends one
bounded local public `SQUARE` request. It rejects non-loopback addresses and
invalid numbers, bounds response frames and has a 10-second response deadline.
The independent Python process test observed `23 → 529` against the Rust peer
and rejection of a non-loopback address. The interop module passed 12/12,
exit 0, using explicit Python 3.12 and Rust 1.88.0 binaries on Windows 11.
Initial invocation via inaccessible WindowsApps `python.exe` failed exit 1
before tests ran. Common checks, review, commit and push remain pending. No
Android/device or private-compute claim follows.

The common `docs`, `workflow` and `rust` profiles passed exit 0 for
`protocol-cli-20261025-001`, with identical before/after source fingerprint
`9c3b53158da21d53ec6e9f998ccdbedfb42e5032b2a2a04a9fb33405312a0896`.
The docs package ran 829 checks; workflow ran 99 tests with two environment
skips. `git diff --check` exited 0. These are pre-commit source checks; the
final changed evidence lines require a refreshed inventory/docs receipt.

Review correction for this follow-up: the 12th Python subprocess case was
written by primary alongside the Rust client. The earlier 11 Python socket
cases were independently authored by the interop peer. The phrase
"independent Python process test" above overstates the 12th case's authorship;
its actual pass/result remains valid. Independent review of the corrected
documentation and latest commit is required.

## Delivery receipt for manual client

The corrected commit `4da68679c36069bb3594e30ba0cab30dbc8fbecd`
received an independent exact-commit security/correctness review with **no
blocker** in the public synthetic loopback scope. Final docs/agent-flow
profile `protocol-cli-review-fix-20261025-001` passed exit 0 (829 package
checks); Rust/workflow and the 12 actual interop cases passed before the
documentation-only correction. `git push origin
HEAD:refs/heads/work/WORK-0015-offline-android-ai` exited 0, and `git
ls-remote --heads origin refs/heads/work/WORK-0015-offline-android-ai`
returned exactly `4da68679c36069bb3594e30ba0cab30dbc8fbecd`, exit 0.
Full WORK-0004, authentication, Android interoperability and privacy
acceptance remain open. This receipt itself is a subsequent metadata change.
