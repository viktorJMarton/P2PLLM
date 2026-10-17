# Architecture

Kotlin UI calls a UniFFI bridge; the Rust runtime composes domain/core ports, storage, transport and backend adapters. CLI uses the same runtime. Core owns state and authorization, platform owns Android lifecycle/permissions and secure key integration. All remote compute paths cross the privacy gate. A gateway/relay forwards protocol traffic but is not trusted with computation plaintext.

Core depends on abstract ports, never concrete libp2p/SQLite/native inference. The runtime is the composition root. Backend interfaces describe supported operation graphs and privacy profiles, not a promise that an entire Qwen graph is supported. Private backend internal multi-party communication must be explicitly adapted/isolated; do not assume a stock MPC library shares the outer connection without integration work.

Initial modules: domain, protocol, node-core, privacy-policy, backend-api, transport-libp2p, storage-sqlite, runtime, node-cli, android-bridge. Model code: learning/reference and native/executorch-adapter. No mandatory llama.cpp module.

Independent substate machines: lifecycle, network, task, update. Model version pinned for every active task. Failed remote execution may retry only under the same privacy constraints. Background operation is a capability controlled by Android; expiry/resource withdrawal is normal.

Diagrams: diagrams/components.puml, diagrams/session.puml, diagrams/learning.puml and diagrams/task-lifecycle.bpmn.
