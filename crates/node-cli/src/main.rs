use p2p_node_core::{Capability, NodeStatus};
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    match args.as_slice() {
        [_, command] if command == "status" => {
            let status = NodeStatus::default();
            let capability = |value| match value {
                Capability::Unavailable => "unavailable",
            };
            println!(
                "{{\"schema_version\":{},\"network_enabled\":{},\"private_compute\":\"{}\",\"private_learning\":\"{}\"}}",
                status.schema_version,
                status.network_enabled,
                capability(status.private_compute),
                capability(status.private_learning)
            );
            ExitCode::SUCCESS
        }
        _ => {
            eprintln!("usage: p2p-node status");
            ExitCode::from(2)
        }
    }
}
