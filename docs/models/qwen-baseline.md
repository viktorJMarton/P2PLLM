# Qwen baseline and operator research

Use Qwen3-0.6B for quick diagnostics, Qwen3-1.7B as a candidate for more useful mobile inference; these are pinned baselines, NOT claims to be latest/best. Resolve exact HF revisions and hashes before downloads; no automatic main-based update. Read each model's license separately. Transformers/PyTorch reference vs ExecuTorch export must be compared for output quality/numeric error.

Verified Qwen3-0.6B config at source inspection: hidden_size=1024, intermediate_size=3072, layers=28, attention_heads=16, kv_heads=8, head_dim=128, activation=silu. Use configuration values directly: do not infer head_dim by hidden_size/head count. Source: https://huggingface.co/Qwen/Qwen3-0.6B/blob/main/config.json . Snapshot is not a locked revision until WORK-0002 resolves it.

Research candidates: linear projections first; attention/KV state and normalization/SiLU/softmax separately. Model masking/rotation is not automatically private. Any local mask correction must be included in cost, including repeated multiplication as costly as original. Keep tokenizer/output handling local in first experiment without claiming hidden activations are safe.

Memory inventory must distinguish weights, quantization metadata, activations, KV cache, backend buffers, OS and training optimizer states. 10 GB device RAM is not 10 GB guaranteed app budget. Full-parameter training, adapter training and inference have different budgets. Measure supported accelerators instead of selecting size solely on RAM.
