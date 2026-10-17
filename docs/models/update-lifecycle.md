# Model and learning update lifecycle

Base model/tokenizer immutable by revision. Personal adapters/knowledge stay local by default; shared updates require enrollment under an approved privacy profile and retention policy. Do not automatically learn from arbitrary peer output or private chat.

Composition ID binds base revision, tokenizer hash, quantization/export config, adapter revisions and runtime compatibility. A session pins the composition. Different peers may keep different versions, but cannot combine incompatible states in one execution. No mandatory global synchronized model or blockchain consensus.

Update: candidate -> evaluating -> approved -> active; rejected or rolled_back alternatives. Evaluate on held-out tasks and regression sets, distinguish quality from consensus/popularity. Partial aggregation can expose individual updates; thresholds and repeated-round leakage belong in security profile.

Atomic activation: stage immutable model artifact; verify hash/compatibility; fsync required artifact; DB transaction updates active composition pointer + journal; restart reconciliation removes orphan staging and resolves incomplete activations. Filesystem and SQLite are not one transaction; simulate crashes at each boundary. Active tasks retain prior composition until completion.
