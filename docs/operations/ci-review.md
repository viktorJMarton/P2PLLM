# CI and review gates

Planned GitHub Actions jobs: docs/schema; Rust format/Clippy/locked tests; Android build/lint/JVM tests; emulator bridge; selected protocol conformance; storage recovery; security path tests. Physical-device accelerator/thermal/energy tests run on designated hardware and carry environment/provenance. Do not treat emulator results as phone NPU results.

Pin actions by full commit SHA and toolchains/dependencies. Untrusted forks run without release secrets; never check out and execute untrusted PR code in privileged pull_request_target jobs. Run public-contribution jobs away from signing credentials/personal devices. Draft bot review cannot grant repository permissions by itself.

Every meaningful PR: WORK link, intended behavior, RFC/ADR references, changed modules, observed tests, known limitations and recovery impact. Clean Code/DRY/local ACID are concrete review questions. Author/pair partner cannot be sole reviewer. Security review for protocol/data/privacy/crypto changes. Math review for partition/scheduler/compression changes, comparing predictions with measurements. Docs-only edits do not trigger expensive model benchmarks.

Review reports bind to exact head commit. New commits invalidate affected conclusions; recheck them. Merge/release automation is disabled until repository policies and owner authority are configured. No assumed human approval for every routine reversible task.
