//! Bounded local diagnostic metadata; no model, prompt or remote payloads.

use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TaskId(String);

impl TaskId {
    pub fn new(value: impl Into<String>) -> Result<Self, TaskError> {
        let value = value.into();
        if value.is_empty()
            || value.len() > 64
            || !value
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
        {
            return Err(TaskError::InvalidId);
        }
        Ok(Self(value))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskState {
    Queued,
    Running,
    Succeeded,
    Failed,
    Cancelled,
    Interrupted,
}

impl TaskState {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Queued => "queued",
            Self::Running => "running",
            Self::Succeeded => "succeeded",
            Self::Failed => "failed",
            Self::Cancelled => "cancelled",
            Self::Interrupted => "interrupted",
        }
    }

    pub fn permits(self, next: Self) -> bool {
        matches!(
            (self, next),
            (Self::Queued, Self::Running | Self::Cancelled)
                | (
                    Self::Running,
                    Self::Succeeded | Self::Failed | Self::Cancelled | Self::Interrupted
                )
        )
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TaskRecord {
    pub id: TaskId,
    pub state: TaskState,
    pub version: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TaskError {
    InvalidId,
    NotFound,
    VersionConflict { expected: u64, actual: u64 },
    InvalidTransition { from: TaskState, to: TaskState },
    Storage(String),
}

impl fmt::Display for TaskError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidId => {
                f.write_str("task ID must contain 1..64 ASCII letters, digits, '_' or '-'")
            }
            Self::NotFound => f.write_str("task not found"),
            Self::VersionConflict { expected, actual } => write!(
                f,
                "task version conflict: expected {expected}, actual {actual}"
            ),
            Self::InvalidTransition { from, to } => write!(
                f,
                "invalid task transition: {} -> {}",
                from.as_str(),
                to.as_str()
            ),
            Self::Storage(message) => write!(f, "task storage error: {message}"),
        }
    }
}

impl std::error::Error for TaskError {}

pub trait TaskStore {
    /// Existing IDs return their current record without adding an event.
    fn create(&mut self, id: &TaskId) -> Result<TaskRecord, TaskError>;
    fn get(&mut self, id: &TaskId) -> Result<Option<TaskRecord>, TaskError>;
    fn list(&mut self) -> Result<Vec<TaskRecord>, TaskError>;
    fn transition(
        &mut self,
        id: &TaskId,
        expected_version: u64,
        next: TaskState,
    ) -> Result<TaskRecord, TaskError>;
    /// Caller must ensure exclusive lifecycle ownership: active tasks of another
    /// process cannot be distinguished from tasks abandoned by a crashed process.
    fn recover_interrupted(&mut self) -> Result<usize, TaskError>;
}

/// Start exactly once or return an existing immutable diagnostic result.
/// A pre-existing Running task requires lifecycle-owner recovery, not retry.
pub fn start_local_diagnostic(
    store: &mut impl TaskStore,
    id: &TaskId,
) -> Result<TaskRecord, TaskError> {
    let record = store.create(id)?;
    match record.state {
        TaskState::Queued => store.transition(id, record.version, TaskState::Running),
        TaskState::Running => Err(TaskError::InvalidTransition {
            from: TaskState::Running,
            to: TaskState::Running,
        }),
        _ => Ok(record),
    }
}

/// Check the actual currently available local node status contract. A successful
/// diagnostic says nothing about model execution or private compute support.
pub fn finish_local_diagnostic(
    store: &mut impl TaskStore,
    running: &TaskRecord,
) -> Result<TaskRecord, TaskError> {
    if running.state != TaskState::Running {
        return Err(TaskError::InvalidTransition {
            from: running.state,
            to: TaskState::Succeeded,
        });
    }
    let status = crate::NodeStatus::default();
    let next = if status.schema_version == 1 {
        TaskState::Succeeded
    } else {
        TaskState::Failed
    };
    store.transition(&running.id, running.version, next)
}

pub fn run_local_diagnostic(
    store: &mut impl TaskStore,
    id: &TaskId,
) -> Result<TaskRecord, TaskError> {
    let record = start_local_diagnostic(store, id)?;
    if record.state == TaskState::Running {
        finish_local_diagnostic(store, &record)
    } else {
        Ok(record)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ids_are_bounded_and_ascii() {
        for bad in ["", "x/y", "two words", "árvíz", &"a".repeat(65)] {
            assert_eq!(TaskId::new(bad), Err(TaskError::InvalidId));
        }
        assert!(TaskId::new("a-Z_09").is_ok());
        assert!(TaskId::new("a".repeat(64)).is_ok());
    }

    #[test]
    fn all_state_pairs_obey_lifecycle() {
        let states = [
            TaskState::Queued,
            TaskState::Running,
            TaskState::Succeeded,
            TaskState::Failed,
            TaskState::Cancelled,
            TaskState::Interrupted,
        ];
        for from in states {
            for to in states {
                let expected = match from {
                    TaskState::Queued => matches!(to, TaskState::Running | TaskState::Cancelled),
                    TaskState::Running => matches!(
                        to,
                        TaskState::Succeeded
                            | TaskState::Failed
                            | TaskState::Cancelled
                            | TaskState::Interrupted
                    ),
                    _ => false,
                };
                assert_eq!(from.permits(to), expected);
            }
        }
    }
}
