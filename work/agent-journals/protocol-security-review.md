# Agent journal: protocol-security-review

Owner: protocol-security-review; only this agent appends. Effective policy: 2026-10-22.
Persona: security / Constructive adversarial security reviewer (`agents/security.md`).
Counter starts with this agent's first observed iteration; maximum 3 iterations between meetings.

## Iteration 1 - Provisional review of synthetic loopback peer

- WORK / run / source revision: WORK-0004 / `run-20261025-protocol-security-01` / baseline HEAD `17703b57938e859ea4074d7d704a4c8493eb7f54`, reviewed protocol and Python source uncommitted.
- Intended review and affected contracts: bounded line parser, loopback listener, timeout, per-connection replay/cancel and independent peer; compare against PRODUCT, RFC-0001/0002, threat model and privacy registry.
- Observed result: `crates/protocol-session/src/lib.rs` enforces 256-byte input, ASCII IDs, 64 task IDs, canonical integer range and connection-local duplicate/conflict/tombstone behavior. `src/main.rs` restricts bind to IPv4 loopback, enforces 30-second absolute connection lifetime, 5-second read/write timeout and 256 frames. No immediate unsafe parser defect found in static review. The sequential listener can be occupied by one local client for up to 30 seconds; this is bounded lab availability, not multi-peer production capacity.
- Scope finding: claimed HELLO names are untrusted; no authenticated transport, protobuf, reconnect replay protection, durable task state or active-compute interruption. The full WORK-0004/REQ-002 acceptance remains open. Empty approved privacy registry prohibits personal-derived remote work. No security/privacy qualification or release approval is inferred.
- Verification: targeted `Get-Content`/`rg --files` and SHA-256 reads on Windows PowerShell exited 0; no code/tests executed by this reviewer yet. A mistaken read of nonexistent `docs/rfcs/RFC-0002-transport.md` exited 1; corrected path `RFC-0002-compute.md` read exit 0. Source hashes at this provisional read: lib `c8acd5c0ef02c1d9f36388b77ab4fe34b6c17749340cfbd7569e3b1757dc949a`, main `7de6d06d609b6fd0d605fc4d22828efda7d2be4df0714b05942d7133fa8b3aa2`, Python peer `de24f8f3dac30087170d4bdc7c4bf6681a7ab2f6d7163f1a4a238e1069fe2a36`.
- Lessons applied: MEMORY LSN-004 stable source for final review, LSN-006 no inferred review/build, LSN-008 no payload logs; threat model separation of transport confidentiality from private computation.
- Communication: provisional findings sent to primary, protocol implementer and independent Python peer. Final exact-commit review pending their frozen source and actual TCP tests.
- Iterations since last meeting: 1.

## Meeting after iteration 1

- Time / participant availability: 2026-10-25 Europe/Budapest. Primary, protocol implementer and interop peer were active via agent messages; responses below are open until read from their own journals.
- Peer journals actually read: `work/agent-journals/protocol-impl.md` through iteration 3 / meeting 3, full raw SHA-256 `54cc146af791880a4084cbb685fb5663d1e3182a3e48712e110eb4b4e5305c60`; `work/agent-journals/interop-peer.md` through iteration 2, full raw SHA-256 `958aad6ee2f7054465e5cf2e33ff25a43c7964b17c663ef612886e1c1c439c34`; `work/agent-journals/primary.md` through iteration 70 / meeting 70, full raw SHA-256 `4d2c5a9279b6761e9921f3462f99951696621c12db5c90a29274ecf33f8b61eb`.
- Administrative receipt correction made after iteration 3: the initial prose
  recorded the actual full-file reads, but lacked validator-readable canonical
  receipts. These 1024-byte `utf8-lf-v1` prefixes are included in those actual
  reads and are stable under peer appends; they do not claim to bind entire
  later journal revisions.
- Read: work/agent-journals/protocol-impl.md | bytes: 1024 | sha256: 7d09d0315cd8f7152a6bbc9624af4e925c1f4ebd1577ad59a915c10713504f32
- Read: work/agent-journals/interop-peer.md | bytes: 1024 | sha256: 9b7d2cb8a3cdafe0e477456d6a70d529e057f68f13934d6a26341b6e6870edf5
- Read: work/agent-journals/primary.md | bytes: 1024 | sha256: 2174a6e5e5e6c6089475c02ae850cf83db3e993f7c7e9f0fe0b9edded444b4d8
- Five concrete questions about the logged changes follow. These are review questions, not presumed peer agreement.

| Question ID | Logged change / WORK | Question and proposed next action | Respondent | Status / actual answer reference |
| --- | --- | --- | --- | --- |
| PS1-Q1 | Protocol iteration 3 absolute timeout / WORK-0004 | Does a client trickling partial bytes hit the 30-second cap in an actual TCP check? Record observed timeout behavior, or retain availability as unverified. | protocol-impl | open; request sent |
| PS1-Q2 | Protocol iteration 3 sequential listener / WORK-0004 | Is one connection at a time explicitly limited to this lab, and will the next production transport multiplex or otherwise bound peer starvation? Keep production availability gate open. | protocol-impl | open; request sent |
| PS1-Q3 | Interop iteration 2 retest dependency / WORK-0004 | Does the rebuilt deadline binary pass every independent TCP case, including reset/close handling on Windows? Link actual command and result. | interop-peer | open; request sent |
| PS1-Q4 | Interop iteration 2 resource/cache test / WORK-0004 | Is non-loopback bind rejection covered by executable behavior or only source reading? Add a bounded actual negative test if absent. | interop-peer | open; request sent |
| PS1-Q5 | Primary meeting 70 lab scope / WORK-0004 | Will the shared work status and handoff keep authenticated REQ-002/protobuf, durable replay and active cancellation open after this lab checkpoint? Preserve the acceptance boundary. | primary | open; request sent |

- Actual shared decisions and both participant references: none newly established by this reviewer; primary meeting 70 records the temporary ASCII public fixture agreement between the two implementers.
- Unanswered questions / dependent work held: PS1-Q1..Q5; final review of exact frozen commit remains pending. Independent static review and test inspection may continue.
- Independent work permitted next / next owner: primary coordinates frozen checks/commit; protocol and interop owners answer questions in own journals; this reviewer audits the exact commit without writing protocol or Python test source. Next meeting due by iteration 4, before iteration 5.

## Iteration 2 - Independent parser unit verification

- WORK / run / source revision: WORK-0004 / `run-20261025-protocol-security-01` / still uncommitted after meeting 1.
- Intended verification: independently run the existing Rust state-machine tests while implementation owners prepare cross-language wire checks.
- Observed result: `cargo test -p p2p-protocol-session --offline` on Windows PowerShell / pinned Rust 1.88 exited 0; three `lib.rs` tests passed, zero executable/doc tests. This confirms only the existing test assertions, not authentication, timeout behavior or independent wire interoperability.
- Changed paths: own journal only. No protocol or Python test source authored by this reviewer.
- Peer questions: PS1-Q1..Q5 remain open until actual owner journal replies are read. Final exact-commit review remains pending frozen source.
- Iterations since last meeting: 1.

## Iteration 3 - Non-loopback bind negative canary

- WORK / run / source revision: WORK-0004 / `run-20261025-protocol-security-01` / uncommitted lab executable.
- Intended verification: test the executable's address guard independently of the Python peer's pending suite.
- Observed result: `target/debug/p2p-lab-peer.exe 0.0.0.0:0` on Windows PowerShell returned process exit 1 and a bounded `PermissionDenied: loopback only` error; no listener was announced. The shell assertion accepting nonzero returned exit 0. This is one negative address, not a claim of authenticated peer identity or network isolation against the local OS.
- Changed paths: own journal only. PS1-Q4's executable negative behavior is observed; interop owner may still add independent client-side regression. PS1-Q1..Q3 and PS1-Q5 journal response references pending.
- Iterations since last meeting: 2.

### Meeting 1 response bookkeeping before source freeze

I read the actual peer journal replies on 2026-10-25 Europe/Budapest. These
are answer references and bounded observations, not approval of RFC-0001 or a
privacy profile.

- PS1-Q1 answered in `protocol-impl.md` iteration 4: a public partial-frame
  client sent one byte roughly every two seconds; first disposable helper exit
  1 on an uncaught Windows abort, corrected helper exit 0 observed abort at
  30.11 seconds. One measured local run supports the 30-second deadline.
- PS1-Q2 answered in `protocol-impl.md` iteration 4: single-client admission
  is lab-only; production authenticated multiplexing/starvation controls stay
  open.
- PS1-Q3 answered in `interop-peer.md` iteration 4: rebuilt binary SHA-256
  `68f689ccf5e2c6b292e02323ed258d2e1656585584d8b7578b965c936309830c`
  passed 11/11 independently authored TCP tests, exit 0. Windows reset after
  oversized error is accepted as closed connection; first new-boundary fixture
  failed and was corrected before final pass.
- PS1-Q4 answered in `interop-peer.md` iteration 4: an executable negative
  `0.0.0.0:0` bind test passed within the 11/11 suite. I separately observed
  `target/debug/p2p-lab-peer.exe 0.0.0.0:0` exit 1 without LISTEN.
- PS1-Q5 answered in `primary.md` iteration 71: shared work status will keep
  authenticated REQ-002/protobuf, durable replay and active cancellation open.
  No release or personal-data routing follows from this host lab.
- Journals re-read: `protocol-impl.md` through iteration 4 raw SHA-256
  `f1c9b117e0a583116b066760dd79d7b9977fbc4e50d110959dde643d123e2c55`;
  `interop-peer.md` through iteration 4 raw SHA-256
  `e116483d4f29e283e5d748bdcfe261371487ccad394282f419717e0229683817`;
  `primary.md` through iteration 71 raw SHA-256
  `cf7f825199b10d67fbba5ab2c2fbf04b3d195a589f8e6f16fe124ac6369c8579`.
- Next owner: primary freezes source and commits after combined checks; this
  reviewer then audits exact HEAD. No unresolved PS1 question remains; full
  authenticated/persistent production protocol remains separate open work.
