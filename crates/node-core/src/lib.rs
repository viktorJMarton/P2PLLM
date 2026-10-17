//! Local node state. Remote AI operations remain unavailable until an approved
//! privacy backend and protocol implementation exist (ADR-003, WORK-0001).

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Capability {
    Unavailable,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct NodeStatus {
    pub schema_version: u32,
    pub network_enabled: bool,
    pub private_compute: Capability,
    pub private_learning: Capability,
}

impl Default for NodeStatus {
    fn default() -> Self {
        Self {
            schema_version: 1,
            network_enabled: false,
            private_compute: Capability::Unavailable,
            private_learning: Capability::Unavailable,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NodeError {
    PrivacyBackendUnavailable,
}

impl NodeStatus {
    pub fn request_private_compute(&self) -> Result<(), NodeError> {
        Err(NodeError::PrivacyBackendUnavailable)
    }

    pub fn request_private_learning(&self) -> Result<(), NodeError> {
        Err(NodeError::PrivacyBackendUnavailable)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unsupported_operations_fail_closed() {
        let node = NodeStatus::default();
        assert!(!node.network_enabled);
        assert_eq!(
            node.request_private_compute(),
            Err(NodeError::PrivacyBackendUnavailable)
        );
        assert_eq!(
            node.request_private_learning(),
            Err(NodeError::PrivacyBackendUnavailable)
        );
    }
}
