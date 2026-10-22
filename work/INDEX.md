# Work queue

WORK-0001 is **in_progress**; WORK-0002–0008 remain **not_started** according to
their briefs. WORK-0009 workflow infrastructure is **verified locally**; Linux
CI and Android/device execution remain unobserved in this work item.
Package preparation is recorded in work/PACKAGE-BUILD.md.

- [WORK-0001: Buildable repository and CI foundation](WORK-0001-project-bootstrap/brief.md) — dependencies: none
- [WORK-0002: Pinned Qwen and accelerator inventory](WORK-0002-model-accelerator-baseline/brief.md) — dependencies: WORK-0001
- [WORK-0003: Privacy threat model and primitive feasibility](WORK-0003-privacy-primitive-selection/brief.md) — dependencies: WORK-0001
- [WORK-0004: Authenticated session and independent peer](WORK-0004-session-conformance/brief.md) — dependencies: WORK-0001
- [WORK-0005: Useful private cooperative AI operation](WORK-0005-private-shared-compute/brief.md) — dependencies: WORK-0002, WORK-0003, WORK-0004
- [WORK-0006: Private adapter round and local activation](WORK-0006-private-shared-learning/brief.md) — dependencies: WORK-0002, WORK-0003, WORK-0004
- [WORK-0007: Android operator UI and contribution lifecycle](WORK-0007-android-operator-mode/brief.md) — dependencies: WORK-0001, WORK-0004
- [WORK-0008: MVP integration and release decision](WORK-0008-release-integration/brief.md) — dependencies: WORK-0005, WORK-0006, WORK-0007

Use briefs for scope, journals/events for observed execution, evidence for reproducibility. WORK-0002–0004 can overlap once dependencies and safe worktrees permit; privacy gate cannot be skipped.

- [WORK-0009: Reproducible department checks and evidence packages](WORK-0009-department-workflows/brief.md) — dependency: existing WORK-0001 scaffold; does not close Android/product gates
- [WORK-0010: Durable local diagnostic task ledger](WORK-0010-local-task-storage/brief.md) — in_progress; local SQL/core/CLI slice, final independent review pending
- [WORK-0011: Android operator navigation and actual status](WORK-0011-android-local-shell/brief.md) — in_progress; Kotlin/native debug APK build observed in WORK-0012; device and final commit review pending
- [WORK-0012: Provisioned development environment](WORK-0012-development-environment/brief.md) — in_progress; pinned Windows tools/doctor and native APK build observed
- [WORK-0013: Full Markdown audit and agent coordination](WORK-0013-agent-flow-audit/brief.md) — in_progress; personas, memory,3-iteration meetings and5-question peer feedback
