# Rust workspace bootstrap

Implemented crates: node-core (capability status and local task port), node-cli
(status and persisted local diagnostics), android-bridge (UniFFI status), and
storage-sqlite (transactional diagnostic metadata). The protocol-session crate
adds a bounded public-fixture TCP loopback lab; it does not authenticate peers
or implement the planned cross-platform transport/runtime. Model/runtime
modules remain unimplemented. See [architecture](../docs/architecture/overview.md)
and [WORK evidence](../work/INDEX.md); compiled Rust code is not a running AI network.
