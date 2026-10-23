use p2p_node_core::{Capability, NodeStatus};

mod diagnostics;
pub use diagnostics::{
    open_local_diagnostics, DiagnosticError, DiagnosticPage, DiagnosticRecord, DiagnosticState,
    LocalDiagnostics,
};

uniffi::setup_scaffolding!();

#[derive(uniffi::Record)]
pub struct BridgeStatus {
    pub schema_version: u32,
    pub network_enabled: bool,
    pub private_compute_available: bool,
    pub private_learning_available: bool,
}

#[uniffi::export]
pub fn node_status() -> BridgeStatus {
    let status = NodeStatus::default();
    BridgeStatus {
        schema_version: status.schema_version,
        network_enabled: status.network_enabled,
        private_compute_available: status.private_compute != Capability::Unavailable,
        private_learning_available: status.private_learning != Capability::Unavailable,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bridge_reports_unavailable_private_operations() {
        let status = node_status();
        assert_eq!(status.schema_version, 1);
        assert!(!status.network_enabled);
        assert!(!status.private_compute_available);
        assert!(!status.private_learning_available);
    }
}
