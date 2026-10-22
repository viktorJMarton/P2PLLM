use p2p_node_core::{Capability, NodeStatus};
use std::process::ExitCode;

mod diagnostics;
mod lease;

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
        [_, command, action, database, id] if command == "diagnostic" && action == "run" => {
            diagnostics::execute(database, diagnostics::Command::Run(id))
        }
        [_, command, action, database] if command == "jobs" && action == "list" => {
            diagnostics::execute(database, diagnostics::Command::List)
        }
        [_, command, action, database, offline]
            if command == "jobs" && action == "recover" && offline == "--offline" =>
        {
            diagnostics::execute(database, diagnostics::Command::Recover)
        }
        _ => {
            eprintln!(
                "usage: p2p-node status\n\
                 p2p-node diagnostic run <database> <nonpersonal-task-id>\n\
                 p2p-node jobs list <database>\n\
                 p2p-node jobs recover <database> --offline\n\
                 Recovery requires all other users of this database to be stopped."
            );
            ExitCode::from(2)
        }
    }
}
