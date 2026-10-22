//! A durable local status diagnostic. No model or peer execution is performed.

use p2p_node_core::tasks::{TaskError, TaskId, TaskRecord, TaskState, TaskStore};
use p2p_node_core::NodeStatus;
use p2p_storage_sqlite::SqliteTaskStore;
use std::process::ExitCode;

pub enum Command<'a> {
    Run(&'a str),
    List,
    Recover,
}

pub fn execute(database: &str, command: Command<'_>) -> ExitCode {
    match execute_inner(database, command) {
        Ok(output) => {
            println!("{output}");
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("Local diagnostic failed: {error}");
            ExitCode::FAILURE
        }
    }
}

fn execute_inner(database: &str, command: Command<'_>) -> Result<String, TaskError> {
    // Validate identifiers before creating a database as a side effect.
    let id = match command {
        Command::Run(value) => Some(TaskId::new(value)?),
        _ => None,
    };
    let lease = crate::lease::DatabaseLease::acquire(database)?;
    let mut store = SqliteTaskStore::open(&lease.database)?;
    match command {
        Command::Run(_) => {
            let record = run_diagnostic(&mut store, id.as_ref().expect("validated run ID"))?;
            Ok(record_json(&record))
        }
        Command::List => Ok(format!(
            "[{}]",
            store
                .list()?
                .iter()
                .map(record_json)
                .collect::<Vec<_>>()
                .join(",")
        )),
        Command::Recover => Ok(format!(
            "{{\"interrupted\":{}}}",
            store.recover_interrupted()?
        )),
    }
}

fn run_diagnostic(store: &mut impl TaskStore, id: &TaskId) -> Result<TaskRecord, TaskError> {
    let record = store.create(id)?;
    match record.state {
        TaskState::Queued => {
            let running = store.transition(id, record.version, TaskState::Running)?;
            // The diagnostic samples actual local status. Unavailable AI is a valid
            // status result; success here describes this diagnostic, never AI work.
            let status = NodeStatus::default();
            let state = if status.schema_version == 1 {
                TaskState::Succeeded
            } else {
                TaskState::Failed
            };
            store.transition(id, running.version, state)
        }
        TaskState::Running => Err(TaskError::InvalidTransition {
            from: TaskState::Running,
            to: TaskState::Running,
        }),
        _ => Ok(record),
    }
}

fn record_json(record: &TaskRecord) -> String {
    // IDs are validated ASCII without quote/backslash/control characters.
    format!(
        "{{\"task_id\":\"{}\",\"kind\":\"local_status_diagnostic\",\"state\":\"{}\",\"version\":{}}}",
        record.id.as_str(), record.state.as_str(), record.version
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn repeated_diagnostic_does_not_advance_completed_task() {
        let mut store = SqliteTaskStore::open(":memory:").unwrap();
        let id = TaskId::new("diagnostic-1").unwrap();
        let first = run_diagnostic(&mut store, &id).unwrap();
        let repeated = run_diagnostic(&mut store, &id).unwrap();
        assert_eq!(first.state, TaskState::Succeeded);
        assert_eq!(first.version, repeated.version);
        assert_eq!(store.events(&id).unwrap().len(), 3);
    }

    #[test]
    fn already_running_diagnostic_requires_explicit_recovery() {
        let mut store = SqliteTaskStore::open(":memory:").unwrap();
        let id = TaskId::new("interrupted-1").unwrap();
        let queued = store.create(&id).unwrap();
        store
            .transition(&id, queued.version, TaskState::Running)
            .unwrap();
        assert!(run_diagnostic(&mut store, &id).is_err());
        assert_eq!(store.recover_interrupted().unwrap(), 1);
        assert_eq!(
            run_diagnostic(&mut store, &id).unwrap().state,
            TaskState::Interrupted
        );
    }
}
