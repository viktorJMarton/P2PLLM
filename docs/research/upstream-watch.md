# Qwen deputy operation

Designed triggers: weekly upstream check; before model/dependency changes; relevant security advisory. No scheduled task/CI workflow is currently installed. When repository scheduling is implemented, use least-privilege discovery job to produce an artifact/proposal, never modify approved versions automatically. No outbound public post required.

Sources: official Qwen model repos/cards/configs and publications; Transformers implementation; ExecuTorch export/backend changes; PEFT learning behavior. Distinguish release/tag, model revision, main branch, preview and unsupported rumor. Capture checked_at and content hash/revision; stale/missing network means unknown, not up to date.

Classify findings watch / experiment / upgrade_proposal / reject. Route operator/architecture changes to math + architecture; training changes to learning; vulnerability/license/serialization to security; export/NPU changes to Android + testing. Upgrade proposal must state affected modules/RFCs, likely benefit, compatibility/license/privacy impact and benchmark plan. Maintain current approved baseline until reviewed tests pass.

Report template: templates/upstream-report.md. Journal reports under the relevant WORK with stable report ID. Human/project agents can query it in IDE by model/version/topic.
