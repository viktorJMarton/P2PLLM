# Work queue

WORK-0001 is **in_progress**; WORK-0002 is the primary active phone-baseline work,
WORK-0003 is active experiment preparation, and WORK-0004–0008 remain **not_started**.
WORK-0009 workflow infrastructure is **verified locally**; Linux
CI and Android/device execution remain unobserved in this work item.
Package preparation is recorded in work/PACKAGE-BUILD.md.

Current sprint: [WORK-0002 capacity/measurement plan](WORK-0002-model-accelerator-baseline/sprint-plan.md).
Owner-selected target: Samsung Galaxy A72 (replaces Honor400Pro); exact hardware
observed SM-A725F/Android14/API34/QTI SM7125/5625888KiB OS-visible RAM in WORK-0002.
Model measurements retain priority; owner2026-10-23 also authorizes parallel
WORK-0014 visible local diagnostic. Privacy preparation is not experimental feasibility.

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
- [WORK-0010: Durable local diagnostic task ledger](WORK-0010-local-task-storage/brief.md) — local source checkpoint22977bb reviewed/tested; Android integration outside delivered scope
- [WORK-0011: Android operator navigation and actual status](WORK-0011-android-local-shell/brief.md) — in_progress; debug APK/lint and final source review observed; Android runtime acceptance pending
- [WORK-0012: Provisioned development environment](WORK-0012-development-environment/brief.md) — in_progress; pinned Windows tools/doctor and native APK build observed
- [WORK-0013: Full Markdown audit and agent coordination](WORK-0013-agent-flow-audit/brief.md) — in_progress; personas, memory,3-iteration meetings and5-question peer feedback
- [WORK-0014: Observable persistent Android diagnostic](WORK-0014-android-persistent-diagnostic/brief.md) — completed bounded diagnostic; reviewed source05768cc pushed/remotely verified; A72 action/persistence passed; versioned0.2.0 APK plus checks delivered to Drive. AI/privacy capabilities remain open

- [WORK-0015: Usable offline Android question and answer](WORK-0015-android-local-inference/brief.md) ? actual A72 visible question/answer and6+2 lifecycle checks passed; source review/push/Drive delivery pending. WORK-0002 numerical/backend and privacy gates remain open.
