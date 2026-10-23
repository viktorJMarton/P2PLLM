# P2P AI Ecosystem — planning baseline 0.1

Open-source, decentralized cooperative AI: shared inference AND shared learning, with privacy as an MVP requirement. Android is the first mobile node; a desktop CLI is the first development partner. The protocol remains implementation-independent.

**Status: development scaffold with a local diagnostic ledger and Android
operator shell with an actionable persistent diagnostic; no running cooperative AI ecosystem.** Host Rust tests, Kotlin
compilation and an ARM64 debug APK build have observed Windows results in
WORK-0010/0012. Phone runtime behavior, model benchmarks, private Qwen execution
and qualified privacy review remain unverified. The privacy backend and
collusion assumptions remain release blockers.

WORK-0014 adds **Helyi ellenőrzés indítása** and saved local history to Android
0.2.0. This checks the local core/storage path; it is not AI inference. Model
export/phone benchmarking remains primary WORK-0002 work. See the actual
[diagnostic scope and evidence](work/WORK-0014-android-persistent-diagnostic/brief.md).

## Start here
1. [Project definition](PRODUCT.md)
2. [Agent entry point](AGENTS.md)
3. [Technology contract](TECHNOLOGY.md)
4. [Canonical decisions](docs/decisions/INDEX.md)
5. [Executable work queue](work/INDEX.md)
6. [Privacy requirements](docs/security/threat-model.md)
7. [Validation and build status](BUILD.md)

Use [environment setup](docs/operations/development-environment.md), the
[work queue](work/INDEX.md) and the selected brief for actual development.
`python tools/validate_package.py` checks source/docs, not runtime behavior.
Agents read [personas](agents/PERSONAS.md), [memory](agents/MEMORY.md) and
[journal meeting rules](docs/operations/agent-meetings.md) before starting.

## Deliverables
Android app, desktop node CLI, protocol specification, backend interfaces, conformance suite, independent test peer, private cooperative computation and learning demonstrations, and reproducible evidence. Public release requires all privacy gates.

## Important boundaries
No NFT/blockchain is required for packet identity. No arbitrary peer-supplied code executes. A secure channel does not hide computation inputs from the computing peer. An advertised NPU is not evidence of supported private arithmetic. A lab benchmark is not an MVP release.

Project license is undecided: this bundle does not grant a license for publication. See [governance](GOVERNANCE.md).

Original design conversation: 2026-10-17, Europe/Budapest. No shareable conversation URL was provided. See [provenance](docs/design-provenance.md).
