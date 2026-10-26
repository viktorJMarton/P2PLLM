# Work queue

The canonical WORK brief status controls dependency eligibility; `verified` requires actual test/review evidence. Package preparation is recorded separately in work/PACKAGE-BUILD.md.

- [WORK-0001: Buildable repository and CI foundation](WORK-0001-project-bootstrap/brief.md) — dependencies: none
- [WORK-0002: Pinned Qwen and accelerator inventory](WORK-0002-model-accelerator-baseline/brief.md) — dependencies: WORK-0001
- [WORK-0003: Privacy threat model and primitive feasibility](WORK-0003-privacy-primitive-selection/brief.md) — dependencies: WORK-0001
- [WORK-0004: Authenticated session and independent peer](WORK-0004-session-conformance/brief.md) — dependencies: WORK-0001
- [WORK-0005: Useful private cooperative AI operation](WORK-0005-private-shared-compute/brief.md) — dependencies: WORK-0002, WORK-0003, WORK-0004
- [WORK-0006: Private adapter round and local activation](WORK-0006-private-shared-learning/brief.md) — dependencies: WORK-0002, WORK-0003, WORK-0004
- [WORK-0007: Android operator UI and contribution lifecycle](WORK-0007-android-operator-mode/brief.md) — dependencies: WORK-0001, WORK-0004
- [WORK-0008: MVP integration and release decision](WORK-0008-release-integration/brief.md) — dependencies: WORK-0005, WORK-0006, WORK-0007

## Automation

The first bounded, opt-in coordinator is [tools/autodev.py](../tools/autodev.py), configured by [config/autodev.tasks.json](../config/autodev.tasks.json). Run `python3 tools/autodev.py plan` before any manual autonomous cycle. For behavior, review gates and meeting outcomes see [autonomous-development.md](../docs/operations/autonomous-development.md). Eligibility is dependency-aware and fails closed; the script does not mark briefs complete or merge branches.

The new product requirements REQ-011–017 and audit findings AUD-001–100 still require explicit per-WORK/test linkage and must not be marked verified solely by this automation.

Use briefs for scope, journals/events for observed execution, evidence for reproducibility. WORK-0002–0004 can overlap once dependencies and safe worktrees permit; privacy gate cannot be skipped.
