# P2P AI Ecosystem — planning baseline 0.1

Open-source, decentralized cooperative AI: shared inference AND shared learning, with privacy as an MVP requirement. Android is the first mobile node; a desktop CLI is the first development partner. The protocol remains implementation-independent.

**Package status: specification and development handoff, not a running AI ecosystem.** No benchmark, private Qwen execution, native Android build, or security audit has been completed. The privacy backend and concrete collusion bound remain release blockers.

## Start here
1. [Project definition](PRODUCT.md)
2. [Agent entry point](AGENTS.md)
3. [Technology contract](TECHNOLOGY.md)
4. [Canonical decisions](docs/decisions/INDEX.md)
5. [Executable work queue](work/INDEX.md)
6. [Privacy requirements](docs/security/threat-model.md)
7. [Validation and build status](BUILD.md)

Run `python3 tools/autodev.py plan` to inspect the next eligible bounded WORK item; the opt-in single-task runner and its limitations are documented in [autonomous development](docs/operations/autonomous-development.md). Run `python3 -m unittest discover -s tests -p 'test_autodev.py'` for its planner tests.\n\nRun `python3 tools/validate_package.py` to validate this handoff package. This does not build or validate the future product. Agent development entry: `work/WORK-0001-project-bootstrap/brief.md`.

## Deliverables
Android app, desktop node CLI, protocol specification, backend interfaces, conformance suite, independent test peer, private cooperative computation and learning demonstrations, and reproducible evidence. Public release requires all privacy gates.

## Important boundaries
No NFT/blockchain is required for packet identity. No arbitrary peer-supplied code executes. A secure channel does not hide computation inputs from the computing peer. An advertised NPU is not evidence of supported private arithmetic. A lab benchmark is not an MVP release.

Project license is undecided: this bundle does not grant a license for publication. See [governance](GOVERNANCE.md).

Original design conversation: 2026-10-17, Europe/Budapest. No shareable conversation URL was provided. See [provenance](docs/design-provenance.md).
