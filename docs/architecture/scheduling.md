# Adaptive scheduling

Filter plans by approved privacy profile, exact model composition compatibility, operation support, memory and owner policy. Score only admissible plans using measured queue + compute + transfer + cryptographic preprocessing/checks + retry cost. Include uncertainty; remote dispatch requires an evidence-supported advantage or enables an otherwise infeasible model operation.

Interactive inference prioritizes response time under fixed energy/bytes/quality limits. Background learning prioritizes useful progress/energy under deadlines. Normalize units before combining objectives; do not sum seconds and joules without declared weights. Initial scheduler is transparent Rust rules/cost model, not an LLM.

Reserve resources with expiry. Freeze participants/model for a safe computation segment; reschedule at defined checkpoints, not every tiny fluctuation. Use hysteresis and cancellation propagation. Never retry to a weaker security mode. Local inference and owner foreground activity have priority; limits/thresholds must be measured, not arbitrary performance claims.

Mathematical role produces prediction intervals, model assumptions and experiments; scheduling logs record sanitized plan choice and measured outcome.
