# Technology contract

Statuses: ACCEPTED = design direction, not installed/verified; CANDIDATE = requires decision; DEFERRED = outside initial implementation.

IMPLEMENTED SLICE means bounded code with platform-specific WORK evidence,
not full product support. Current toolchain lock/setup is documented in
docs/operations/development-environment.md; Windows JDK17.0.20.1 and Android
build results do not establish Linux/device/privacy behavior. Tokio, transport
and inference adapters remain design choices until their code/evidence exists.

| Component | Choice | Status |
|---|---|---|
| Android UI/platform | Kotlin, Jetpack Compose, Android SDK/NDK, Gradle wrapper | ACCEPTED |
| Node core / CLI | Rust stable, Tokio, Cargo workspace | ACCEPTED |
| P2P adapter | rust-libp2p; QUIC primary candidate, TCP + Noise/Yamux fallback candidate | ACCEPTED library, transport matrix to verify |
| Kotlin bindings | UniFFI | ACCEPTED, Android smoke build required |
| ML research/training/reference | Python, PyTorch, Hugging Face Transformers, PEFT for adapter experiments | ACCEPTED |
| Mobile inference | ExecuTorch, supported export/backend path | ACCEPTED, each model/device requires validation |
| Models | Qwen3-0.6B diagnostic; Qwen3-1.7B useful mobile candidate | ACCEPTED baseline / candidate, pin revisions before code |
| Local persistence | SQLite owned by node core, migrations | ACCEPTED |
| Local diagnostic storage adapter | rusqlite =0.32.1 with bundled libsqlite3-sys 0.30.1; CLI lifecycle lock fs2 =0.4.3 | IMPLEMENTED slice, Windows tests in WORK-0010; final review pending |
| Wire control schema | protobuf; Rust prost proposed | ACCEPTED schema direction, crate version pin pending |
| Configuration | TOML typed/validated, no embedded secrets | ACCEPTED |
| CI | GitHub Actions; actions pinned by SHA | ACCEPTED when a repository exists |
| Private computation | MP-SPDZ reference MPC; OpenFHE comparison | CANDIDATE, release blocker |
| Private training | secure aggregation + explicit DP accounting where required | CANDIDATE, no selected audited implementation |
| Local inference comparison | llama.cpp | OPTIONAL benchmark only, superseded as main runtime |
| Drive tooling | rclone-backed explicit snapshot import/export | ACCEPTED design, login/setup not performed |

## Version policy
Do not use latest.release or unpinned git main in builds. Bootstrap resolves a compatible tested toolchain, records exact versions in rust-toolchain.toml, Cargo.lock, Gradle wrapper/dependency locks and a Python lockfile, and adds dependency provenance. This package intentionally does not invent verified versions.

## Accelerator policy
Inventory CPU/GPU/NPU/DSP and backend availability. Compile/export and run a supported operation before claiming acceleration. Measure CPU fallback and transfer overhead. Qualcomm QNN and other vendor backends are device-dependent and may introduce non-open binary dependencies; record license, redistribution and hardware constraints. ISP is a fixed camera pipeline, not assumed general-purpose compute. No unnecessary camera permission. Training/private arithmetic support is distinct from inference acceleration.

## Architectural restriction
ExecuTorch export does not automatically partition private computation, support arbitrary online training, or run MPC arithmetic on an NPU. Do not promise zero-copy across Rust/Kotlin/native boundaries until measured. No public exposure of raw llama.cpp RPC. No archived privacy ML project is adopted solely because it uses PyTorch.
