# Public loopback protocol lab

This crate runs one synthetic `SQUARE` operation over plain TCP on
`127.0.0.1`. It is a temporary interoperability fixture for WORK-0004, not the
authenticated protobuf/QUIC session in RFC-0001/0002. `HELLO` names are claimed
strings, not verified identities. Do not send personal-derived inputs or expose
the listener outside loopback.

Run `cargo run -p p2p-protocol-session --bin p2p-lab-peer -- 127.0.0.1:0`.
The first stdout line is `LISTEN 127.0.0.1:<port>`. At most eight connections
are served concurrently. An accepted connection occupies a slot even before
HELLO; a ninth is closed immediately without a protocol response or worker.
Each client has a 30-second absolute session deadline, a five-second per-read
timeout and a 256-frame cap. Results and cancellation tombstones expire on
disconnect.

To try the public fixture manually, keep the peer running and use its printed
port with `cargo run -p p2p-protocol-session --bin p2p-lab-client --
127.0.0.1:<port> 23`. The client prints `529` on a valid reply and exits
nonzero on an invalid or missing reply. It accepts only IPv4 loopback and a
canonical integer in `0..=1000000`; it does not send arbitrary prompts.

Frames are ASCII with one LF, maximum 256 bytes including LF. No CR or extra
spaces are accepted. The client first sends `P2P1 HELLO <id>` and receives
`P2P1 HELLO lab-peer`. IDs contain 1–32 ASCII letters, digits, `_` or `-`.
Subsequent commands are:

| Request | Response |
| --- | --- |
| `P2P1 OFFER <id> SQUARE <n>` | `P2P1 RESULT <id> <n*n>` |
| Same ID and `n` | Cached result, or `P2P1 CANCELLED <id>` if cancelled |
| Same ID, different `n` | `P2P1 ERROR STEP_CONFLICT` |
| `P2P1 CANCEL <id>` | `P2P1 CANCELLED <id>`; unseen ID reserves a tombstone |

`n` is canonical unsigned decimal in `0..=1000000`. At most 64 distinct IDs
are held per connection. A 65th ID returns `P2P1 ERROR RESOURCE_LIMIT` and
leaves existing IDs available. Unsupported syntax returns
`OPERATION_UNSUPPORTED`; other major versions return `VERSION_UNSUPPORTED`
and close. A frame exceeding 256 bytes, or reaching 256 bytes without LF,
returns `RESOURCE_LIMIT` and closes. A partial frame followed by EOF, socket
read timeout or session deadline closes without a protocol error response.
No result is persisted, and this synchronous operation has no active compute
to interrupt. These limits are lab settings, not production security bounds.
