# RFC-0002 — bounded compute tasks (draft)

Messages TASK_OFFER, TASK_ACCEPT/REJECT, COMPUTE_STEP, STEP_RESULT, TASK_STATUS, TASK_END, ERROR. Schema sketch: schemas/protocol/v1/session.proto. It is a draft, not a deployable complete cryptographic wire format.

Offer binds operation allowlist entry, immutable model composition, privacy profile/version, resource budget/deadline and expected input/output descriptors. Sender does not supply arbitrary code or operator graph. Profile may require multiple participants and setup; a two-node demo does not satisfy all MPC profiles.

(task_id, step_id) identifies a step; request digest binds exact accepted request bytes and profile context. Duplicate same ID/digest returns cached status/result or a defined expired state; same ID/different digest rejects. Do not reexecute stateful KV-cache steps silently. Persist task transitions transactionally; result retention bounded. Resume only when backend state/checkpoint and profile permit it; otherwise restart a new task/session safely.

Validate tensor element count, shape/dtype and byte length before allocation; ciphertext/share descriptors differ from plaintext tensors. No arbitrary automatic decryption. Payload integrity hash is not proof of correct compute. Private backend correctness, challenge tests and threat model are separate.

Errors: VERSION_UNSUPPORTED, MODEL_INCOMPATIBLE, OPERATION_UNSUPPORTED, PRIVACY_PROFILE_UNAVAILABLE, RESOURCE_LIMIT, DEADLINE_EXCEEDED, STEP_CONFLICT, STATE_EXPIRED, BACKEND_FAILURE, CANCELLED. Errors reveal no private payload. Cancellation/peer dropout propagate to all affected substeps.
