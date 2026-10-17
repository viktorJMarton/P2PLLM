# Interface contract — draft

UI/CLI -> core asynchronous commands: start_node, stop_node, set_network_enabled, set_contribution_policy, load_model, submit_inference, cancel_task, evaluate_update, activate_update, rollback_update. Accepted commands return operation/task ID, not completion. get_snapshot returns versioned state; subscribe_events supports bounded buffering and resync after a gap.

Events: TaskStarted/Progress/Completed/Failed, NetworkStateChanged, ResourceLimitReached, UpdateEvaluationCompleted. Every event has event/run/task correlation where relevant, timestamp and monotonically increasing local sequence. Never embed sensitive payloads in audit events.

Backend ports: inspect_capabilities; prepare(model_manifest, operation, security_profile); execute_step(opaque_input_handle, budget, cancellation); release(task). Learning: enroll(round_contract); train_local; protected_aggregate; evaluate; propose_update. Plain tensors and cryptographic shares/ciphertexts are different types and must not be implicitly converted.

Identity/keystore port: public_identity; sign/challenge; scoped secret storage. Android Keystore algorithm support may not match libp2p identity key needs: validate signing support or use a Keystore wrapping key for an encrypted software identity; do not claim non-exportable peer keys without evidence.

Resource port: memory/thermal/battery/connection observations and explicit reservations. Storage port: transactional task/event update, composition activation record, recovery checkpoint. Deadline durations use monotonic time locally; wire expiry includes skew policy.
