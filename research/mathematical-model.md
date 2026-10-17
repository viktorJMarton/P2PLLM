# Initial performance model (hypothesis)

For serial remote substep: T_total = T_queue + T_local + T_setup + T_crypto_preprocess + B_up/R_up + B_down/R_down + N_rounds*RTT + T_remote + T_verify + T_recovery. Time seconds; B bytes; R bytes/second; RTT seconds. Avoid double-counting transfer and round measurements. Warm/cold setup separated; overlap/pipeline use a task graph critical path, not the serial sum.

Compare same operation, quality, security and available memory. Report median and tail latency with sample count/uncertainty, device state and queue conditions. Weighted objectives must normalize seconds/joules/bytes or express explicit constraints. A model is not a measurement and a simulation is not a cryptographic proof.

Expected retry model needs independence assumptions; phone failures may correlate with thermal/network events. DP/privacy budgets are not converted to milliseconds in a soft score; security admissibility is a hard constraint.

Break-even: protected remote plan is useful if lower measured end-to-end cost or enables a required otherwise infeasible operation under fixed bounds. No assumed universal speedup.
