# WORK-0004 bounded loopback lab handoff

Status: implemented and tested **host-only synthetic lab slice**; full WORK-0004
acceptance open. Run `run-20261025-protocol-loopback-01`, source baseline
`17703b57938e859ea4074d7d704a4c8493eb7f54`, branch
`work/WORK-0015-offline-android-ai`. Commit and remote verification are recorded
in the work journal when they actually occur.

The new `crates/protocol-session` Rust crate runs a separate `p2p-lab-peer`
binary. It binds only `127.0.0.1`, accepts a claimed HELLO name and executes
one deterministic public `SQUARE` task through capped ASCII/LF frames. It
handles same-ID replay, conflicting input, cancellation tombstones, a 64-ID
cache and one-connection expiry. The TCP adapter limits frames to 256 bytes,
connections to 256 frames and 30 seconds, with five-second read/write waits.
The [crate README](../../crates/protocol-session/README.md) states the wire.

A follow-up `p2p-lab-client` binary provides a manual public-fixture path:
connect to the printed local port and run `SQUARE 23` to see `529`. The client
accepts only IPv4 loopback and bounded canonical integers, validates the
expected HELLO/RESULT, and bounds response time and frame size. Its process
interop case passed with the Rust peer. This is a local lab aid, not an
authenticated cross-platform peer or AI task.

This is a temporary fixture separate from the draft
[session schema](../../schemas/protocol/v1/session.proto) and
[RFC-0001](../../docs/rfcs/RFC-0001-session.md). Plain loopback TCP and HELLO
names do not authenticate a peer or protect personal data. It cannot accept
personal-derived input. Synchronous `SQUARE` finishes before CANCEL, so the
current tombstone does not demonstrate interruption of active AI work. No
cross-session durable replay prevention or long-lived connection management is
implemented. A single local client can occupy the sequential listener until
its deadline; production availability is unmeasured.

The protocol implementer built the crate with no new external dependency:
`cargo test -p p2p-protocol-session --offline` passed three unit tests, `cargo
fmt --all --check` and `cargo clippy -p p2p-protocol-session --all-targets
--offline -- -D warnings` exited zero, and the debug binary built. The
independently written [Python peer](../../tests/interop/test_p2p_lab_peer.py)
opened actual sockets to the Rust process. Its final 11/11 test run exited
zero on Windows/Python 3.12 against the rebuilt binary: happy path, duplicate,
conflict, version mismatch, oversized and exact-boundary frames, fragmentation,
cancel before/after result, per-connection cache, 65th ID rejection and
non-loopback bind rejection. Earlier 8/9 and failed 11-case harness attempts
remain in the agents' journals; they were repaired before the final result.
The tests send only fixed synthetic numbers and IDs. Exact final commands,
binary/test hashes, source fingerprint and combined-check outcome belong in
the [work journal](journal.md) after the source is frozen.

Independent security review provisionally found no unsafe parser blocker in
this public lab scope. Exact-commit security review and the applicable combined
checks are still required before bounded closure. Full WORK-0004 acceptance
remains open: real authenticated transport/identity, protobuf and versioned
capability negotiation, malformed-message/replay conformance across reconnect,
active-task cancellation/recovery, independently implemented peer conformance
on Android and desktop, and actual resource/connectivity measurements. The
empty [privacy registry](../../docs/security/privacy-profile-registry.md)
still blocks personal-derived remote work. This lab neither proves private
computation nor advances the WORK-0003 backend gate.

The manual CLI checkpoint is commit
`4da68679c36069bb3594e30ba0cab30dbc8fbecd` on the existing development
branch, remote SHA verified. The latest-commit independent review found no
blocker for this public lab only. Its newly added Python subprocess case was
authored by primary; the earlier 11 socket cases were separately authored by
the interop peer. WORK-0004 remains in progress with the gates above.

Next host-lab increment (`run-20261025-protocol-concurrency-03`) admits at
most eight simultaneous localhost clients. A ninth gets no protocol reply;
released slots can be reused. The separately authored Python peer observed
14/14 actual process/socket passes, including two new concurrency/admission
cases; the suite includes one primary-authored Rust-CLI process case. This
increment is uncommitted pending combined checks and exact-commit review at
this handoff update; it changes lab availability, not authentication or the
privacy gate.

Concurrent-lab source checkpoint `94feb94286408d4f9b33f122cdd2604e3c038776`
received independent exact-commit review with no blocker for public localhost
fixtures, was pushed to `work/WORK-0015-offline-android-ai`, and the remote
SHA was verified equal. Reviewer reran 14/14 TCP cases. WORK-0004 and its
authentication, Android/Linux interop, active cancellation and privacy gates
remain open; this receipt follows the reviewed source commit.
