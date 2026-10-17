# RFC-0001 — authenticated session (draft)

HELLO negotiates protocol and authenticated identity after transport handshake; CAPABILITIES advertises supported operations, model composition and profile IDs. Capabilities are untrusted offers. Local policy validates approved implementation/profile plus participant assumptions before acceptance. A peer pair keeps one logical persistent association; multiplex streams so control/cancel is not blocked behind huge payloads. Physical connection count is implementation detail; no global single connection or all-peer full mesh requirement.

Define bounded control/payload frames, maximum in-flight bytes, flow control, timeouts, local monotonic deadline and skew policy. Numbers are tuned and recorded, not security proof. Version major mismatch rejects; unknown security-critical fields/modes reject; unknown harmless optional fields may be ignored as specified. Transcript/model/profile binding prevents mismatched negotiation. Use established authenticated transport, not custom crypto.

Connection discovery is separate: bootstrap/relay helps connectivity. Discovery and optional topic reputation index are not global truth. No periodic full index broadcast. Metadata/IP visibility is explicitly not anonymity. Session expiry/reconnect requires fresh authentication; old replayed messages cannot create fresh compute authorization.
