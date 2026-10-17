# M1 — protected cooperative computation

Start from a pinned PyTorch reference operation (public-weight linear map, then a block) and candidate MPC/FHE implementation. Record what is secret/public and what output the requester is entitled to learn. Model weights may be public; activations remain private. Include local masking/correction, preprocessing and output verification costs.

Run desktop primitive reference, Android build feasibility, then Android+desktop with real cryptographic backend. For methods requiring more parties, add processes/hosts and explicitly mark correlated-host lab assumptions. Do not claim multiple processes on one host prove independent trust.

Plaintext layer splitting of Qwen is allowed only as a labeled synthetic comparison, never private mode. Expand supported operations only after threat-model review, numeric equivalence and total cost analysis. Measure warm/cold latency, first token time when full generation exists, tokens/s only for real generation, bytes/op, peak memory, energy with method and thermal state, failure/abort. Avoid byte/token metrics on a primitive lacking tokens.

MVP acceptance is useful private AI computation, not just a secure addition. Negative feasibility result is valid research; it blocks release, not privacy policy relaxation.
