//! SQLite local diagnostic ledger. Recovery is explicit and requires exclusive
//! lifecycle ownership; opening a connection never interrupts active work.

pub mod lease;

use std::{path::Path, time::Duration};

use p2p_node_core::tasks::{TaskError, TaskId, TaskRecord, TaskState, TaskStore};
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};

const SCHEMA_VERSION: i64 = 1;
pub const MAX_DIAGNOSTIC_PAGE_SIZE: u32 = 50;
pub const MAX_DIAGNOSTIC_OFFSET: u32 = 10_000;

pub struct TaskPage {
    pub records: Vec<TaskRecord>,
    pub next_offset: Option<u32>,
}

pub struct SqliteTaskStore {
    connection: Connection,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TaskEvent {
    pub sequence: u64,
    pub task_id: TaskId,
    pub state: TaskState,
    pub version: u64,
}

fn storage(error: impl std::fmt::Display) -> TaskError {
    // SQLite diagnostics contain schema/IO information, never task payloads.
    TaskError::Storage(error.to_string())
}

fn decode_state(value: &str) -> Result<TaskState, TaskError> {
    match value {
        "queued" => Ok(TaskState::Queued),
        "running" => Ok(TaskState::Running),
        "succeeded" => Ok(TaskState::Succeeded),
        "failed" => Ok(TaskState::Failed),
        "cancelled" => Ok(TaskState::Cancelled),
        "interrupted" => Ok(TaskState::Interrupted),
        _ => Err(storage("unrecognized stored task state")),
    }
}

fn decode_record(raw: (String, String, i64)) -> Result<TaskRecord, TaskError> {
    Ok(TaskRecord {
        id: TaskId::new(raw.0).map_err(|_| storage("invalid stored task ID"))?,
        state: decode_state(&raw.1)?,
        version: u64::try_from(raw.2).map_err(|_| storage("invalid stored task version"))?,
    })
}

fn get_record(connection: &Connection, id: &TaskId) -> Result<Option<TaskRecord>, TaskError> {
    let raw = connection
        .query_row(
            "SELECT id, state, version FROM tasks WHERE id = ?1",
            [id.as_str()],
            |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
        )
        .optional()
        .map_err(storage)?;
    raw.map(decode_record).transpose()
}

fn list_records(connection: &Connection, running_only: bool) -> Result<Vec<TaskRecord>, TaskError> {
    let sql = if running_only {
        "SELECT id, state, version FROM tasks WHERE state = 'running' ORDER BY id"
    } else {
        "SELECT id, state, version FROM tasks ORDER BY id"
    };
    let mut query = connection.prepare(sql).map_err(storage)?;
    let rows = query
        .query_map([], |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)))
        .map_err(storage)?;
    rows.map(|row| decode_record(row.map_err(storage)?))
        .collect()
}

fn append_event(connection: &Connection, record: &TaskRecord) -> Result<(), TaskError> {
    let version = i64::try_from(record.version).map_err(|_| storage("task version overflow"))?;
    connection
        .execute(
            "INSERT INTO task_events(task_id, state, version) VALUES (?1, ?2, ?3)",
            params![record.id.as_str(), record.state.as_str(), version],
        )
        .map_err(storage)?;
    Ok(())
}

fn change_record(
    connection: &Connection,
    id: &TaskId,
    expected_version: u64,
    next: TaskState,
) -> Result<TaskRecord, TaskError> {
    let current = get_record(connection, id)?.ok_or(TaskError::NotFound)?;
    if current.version != expected_version {
        return Err(TaskError::VersionConflict {
            expected: expected_version,
            actual: current.version,
        });
    }
    if !current.state.permits(next) {
        return Err(TaskError::InvalidTransition {
            from: current.state,
            to: next,
        });
    }
    let version = current
        .version
        .checked_add(1)
        .filter(|v| *v <= i64::MAX as u64)
        .ok_or_else(|| storage("task version overflow"))?;
    let changed = connection
        .execute(
            "UPDATE tasks SET state = ?1, version = ?2 WHERE id = ?3 AND version = ?4",
            params![
                next.as_str(),
                version as i64,
                id.as_str(),
                expected_version as i64
            ],
        )
        .map_err(storage)?;
    if changed != 1 {
        return Err(storage(
            "task compare-and-set failed inside write transaction",
        ));
    }
    let record = TaskRecord {
        id: id.clone(),
        state: next,
        version,
    };
    append_event(connection, &record)?;
    Ok(record)
}

impl SqliteTaskStore {
    /// ID-ordered bounded page, not a stable snapshot across separate calls.
    /// next_offset also stops at the traversal bound, even if more rows exist.
    pub fn list_page(&self, limit: u32, offset: u32) -> Result<TaskPage, TaskError> {
        if !(1..=MAX_DIAGNOSTIC_PAGE_SIZE).contains(&limit) || offset > MAX_DIAGNOSTIC_OFFSET {
            return Err(storage("invalid diagnostic page bounds"));
        }
        let mut statement = self
            .connection
            .prepare("SELECT id, state, version FROM tasks ORDER BY id LIMIT ?1 OFFSET ?2")
            .map_err(storage)?;
        let rows = statement
            .query_map(params![i64::from(limit) + 1, i64::from(offset)], |row| {
                Ok((row.get(0)?, row.get(1)?, row.get(2)?))
            })
            .map_err(storage)?;
        let mut records: Vec<TaskRecord> = rows
            .map(|row| decode_record(row.map_err(storage)?))
            .collect::<Result<_, _>>()?;
        let has_more = records.len() > limit as usize;
        records.truncate(limit as usize);
        let next_offset = offset
            .checked_add(limit)
            .filter(|next| has_more && *next <= MAX_DIAGNOSTIC_OFFSET);
        Ok(TaskPage {
            records,
            next_offset,
        })
    }

    pub fn open(path: impl AsRef<Path>) -> Result<Self, TaskError> {
        let mut connection = Connection::open(path).map_err(storage)?;
        connection
            .busy_timeout(Duration::from_secs(5))
            .map_err(storage)?;
        connection
            .execute_batch("PRAGMA foreign_keys = ON; PRAGMA synchronous = FULL;")
            .map_err(storage)?;
        let transaction = connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(storage)?;
        let version: i64 = transaction
            .pragma_query_value(None, "user_version", |r| r.get(0))
            .map_err(storage)?;
        if !(0..=SCHEMA_VERSION).contains(&version) {
            return Err(storage("unsupported SQLite schema version"));
        }
        if version == 0 {
            transaction.execute_batch(
                "CREATE TABLE tasks (
                    id TEXT PRIMARY KEY NOT NULL CHECK(length(id) BETWEEN 1 AND 64 AND id NOT GLOB '*[^a-zA-Z0-9_-]*'),
                    state TEXT NOT NULL CHECK(state IN ('queued','running','succeeded','failed','cancelled','interrupted')),
                    version INTEGER NOT NULL CHECK(version >= 0)
                 );
                 CREATE TABLE task_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES tasks(id),
                    state TEXT NOT NULL CHECK(state IN ('queued','running','succeeded','failed','cancelled','interrupted')),
                    version INTEGER NOT NULL CHECK(version >= 0),
                    UNIQUE(task_id, version)
                 );
                 PRAGMA user_version = 1;"
            ).map_err(storage)?;
        }
        transaction.commit().map_err(storage)?;
        Ok(Self { connection })
    }

    pub fn events(&self, id: &TaskId) -> Result<Vec<TaskEvent>, TaskError> {
        let mut statement = self.connection.prepare(
            "SELECT sequence, state, version FROM task_events WHERE task_id = ?1 ORDER BY sequence"
        ).map_err(storage)?;
        let rows = statement
            .query_map([id.as_str()], |row| {
                Ok((
                    row.get::<_, i64>(0)?,
                    row.get::<_, String>(1)?,
                    row.get::<_, i64>(2)?,
                ))
            })
            .map_err(storage)?;
        rows.map(|row| {
            let (sequence, state, version) = row.map_err(storage)?;
            Ok(TaskEvent {
                sequence: u64::try_from(sequence).map_err(|_| storage("invalid event sequence"))?,
                task_id: id.clone(),
                state: decode_state(&state)?,
                version: u64::try_from(version).map_err(|_| storage("invalid event version"))?,
            })
        })
        .collect()
    }
}

impl TaskStore for SqliteTaskStore {
    fn create(&mut self, id: &TaskId) -> Result<TaskRecord, TaskError> {
        let tx = self
            .connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(storage)?;
        let record = if let Some(existing) = get_record(&tx, id)? {
            existing
        } else {
            let record = TaskRecord {
                id: id.clone(),
                state: TaskState::Queued,
                version: 0,
            };
            tx.execute(
                "INSERT INTO tasks(id,state,version) VALUES (?1,'queued',0)",
                [id.as_str()],
            )
            .map_err(storage)?;
            append_event(&tx, &record)?;
            record
        };
        tx.commit().map_err(storage)?;
        Ok(record)
    }

    fn get(&mut self, id: &TaskId) -> Result<Option<TaskRecord>, TaskError> {
        get_record(&self.connection, id)
    }

    fn list(&mut self) -> Result<Vec<TaskRecord>, TaskError> {
        list_records(&self.connection, false)
    }

    fn transition(
        &mut self,
        id: &TaskId,
        expected_version: u64,
        next: TaskState,
    ) -> Result<TaskRecord, TaskError> {
        let tx = self
            .connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(storage)?;
        let record = change_record(&tx, id, expected_version, next)?;
        tx.commit().map_err(storage)?;
        Ok(record)
    }

    fn recover_interrupted(&mut self) -> Result<usize, TaskError> {
        let tx = self
            .connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(storage)?;
        let running = list_records(&tx, true)?;
        for task in &running {
            change_record(&tx, &task.id, task.version, TaskState::Interrupted)?;
        }
        tx.commit().map_err(storage)?;
        Ok(running.len())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};

    struct TestDatabase(std::path::PathBuf);

    impl TestDatabase {
        fn new() -> Self {
            static NEXT: AtomicU64 = AtomicU64::new(0);
            Self(std::env::temp_dir().join(format!(
                "p2p-ledger-test-{}-{}.sqlite",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            )))
        }
        fn open(&self) -> SqliteTaskStore {
            SqliteTaskStore::open(&self.0).unwrap()
        }
    }

    impl Drop for TestDatabase {
        fn drop(&mut self) {
            let _ = std::fs::remove_file(&self.0);
        }
    }

    fn id(value: &str) -> TaskId {
        TaskId::new(value).unwrap()
    }

    #[test]
    fn sql_pages_are_bounded_and_stop_at_explicit_traversal_limit() {
        let mut store = SqliteTaskStore::open(":memory:").unwrap();
        {
            let transaction = store.connection.transaction().unwrap();
            {
                let mut statement = transaction
                    .prepare("INSERT INTO tasks(id,state,version) VALUES (?1,'queued',0)")
                    .unwrap();
                for index in 0..10_052 {
                    statement.execute([format!("job-{index:05}")]).unwrap();
                }
            }
            transaction.commit().unwrap();
        }
        let first = store.list_page(50, 0).unwrap();
        assert_eq!(first.records.len(), 50);
        assert_eq!(first.records[0].id.as_str(), "job-00000");
        assert_eq!(first.records[49].id.as_str(), "job-00049");
        assert_eq!(first.next_offset, Some(50));
        let bound = store.list_page(50, 10_000).unwrap();
        assert_eq!(bound.records.len(), 50);
        assert_eq!(bound.records[0].id.as_str(), "job-10000");
        assert_eq!(bound.next_offset, None);
        assert!(store.list_page(0, 0).is_err());
        assert!(store.list_page(51, 0).is_err());
        assert!(store.list_page(1, 10_001).is_err());
    }

    #[test]
    fn create_is_idempotent_at_current_state_and_events_are_ordered() {
        let mut store = SqliteTaskStore::open(":memory:").unwrap();
        let task = id("diagnostic-1");
        assert_eq!(store.create(&task).unwrap().version, 0);
        let running = store.transition(&task, 0, TaskState::Running).unwrap();
        assert_eq!(store.create(&task).unwrap(), running);
        let done = store.transition(&task, 1, TaskState::Succeeded).unwrap();
        assert_eq!(store.create(&task).unwrap(), done);
        let events = store.events(&task).unwrap();
        assert_eq!(
            events.iter().map(|e| e.version).collect::<Vec<_>>(),
            vec![0, 1, 2]
        );
        assert!(events.windows(2).all(|w| w[0].sequence < w[1].sequence));
        assert_eq!(store.list().unwrap(), vec![done]);
        assert!(matches!(
            store.transition(&task, 2, TaskState::Running),
            Err(TaskError::InvalidTransition { .. })
        ));
        assert!(matches!(
            store.transition(&id("absent"), 0, TaskState::Running),
            Err(TaskError::NotFound)
        ));
        assert!(store.get(&id("absent")).unwrap().is_none());
    }

    #[test]
    fn separate_connections_reject_stale_versions() {
        let db = TestDatabase::new();
        let mut first = db.open();
        let mut second = db.open();
        let task = id("same-task");
        first.create(&task).unwrap();
        let stale = second.get(&task).unwrap().unwrap();
        first.transition(&task, 0, TaskState::Running).unwrap();
        assert_eq!(
            second.transition(&task, stale.version, TaskState::Cancelled),
            Err(TaskError::VersionConflict {
                expected: 0,
                actual: 1
            })
        );
        assert_eq!(second.events(&task).unwrap().len(), 2);
    }

    #[test]
    fn concurrent_writers_commit_exactly_one_transition() {
        let db = TestDatabase::new();
        db.open().create(&id("contended")).unwrap();
        let barrier = std::sync::Arc::new(std::sync::Barrier::new(2));
        let threads: Vec<_> = [TaskState::Running, TaskState::Cancelled]
            .into_iter()
            .map(|next| {
                let path = db.0.clone();
                let barrier = barrier.clone();
                std::thread::spawn(move || {
                    let mut store = SqliteTaskStore::open(path).unwrap();
                    barrier.wait();
                    store.transition(&id("contended"), 0, next)
                })
            })
            .collect();
        let results: Vec<_> = threads
            .into_iter()
            .map(|thread| thread.join().unwrap())
            .collect();
        assert_eq!(results.iter().filter(|result| result.is_ok()).count(), 1);
        assert_eq!(
            results
                .iter()
                .filter(|result| matches!(
                    result,
                    Err(TaskError::VersionConflict {
                        expected: 0,
                        actual: 1
                    })
                ))
                .count(),
            1
        );
        assert_eq!(db.open().events(&id("contended")).unwrap().len(), 2);
    }

    #[test]
    fn process_crash_helper() {
        let Some(path) = std::env::var_os("P2P_LEDGER_CRASH_TEST_DATABASE") else {
            return;
        };
        let mut store = SqliteTaskStore::open(path).unwrap();
        let transaction = store
            .connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .unwrap();
        change_record(&transaction, &id("crashed"), 1, TaskState::Succeeded).unwrap();
        transaction
            .execute(
                "INSERT INTO tasks(id,state,version) VALUES ('uncommitted','queued',0)",
                [],
            )
            .unwrap();
        append_event(
            &transaction,
            &TaskRecord {
                id: id("uncommitted"),
                state: TaskState::Queued,
                version: 0,
            },
        )
        .unwrap();
        // Deliberately bypass Connection/Transaction destructors before commit.
        std::process::exit(97);
    }

    #[test]
    fn process_exit_before_commit_rolls_back_then_explicit_recovery_works() {
        let db = TestDatabase::new();
        {
            let mut store = db.open();
            store.create(&id("crashed")).unwrap();
            store
                .transition(&id("crashed"), 0, TaskState::Running)
                .unwrap();
        }
        let output = std::process::Command::new(std::env::current_exe().unwrap())
            .args(["--exact", "tests::process_crash_helper", "--nocapture"])
            .env("P2P_LEDGER_CRASH_TEST_DATABASE", &db.0)
            .output()
            .unwrap();
        assert_eq!(
            output.status.code(),
            Some(97),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        let mut store = db.open();
        assert!(store.get(&id("uncommitted")).unwrap().is_none());
        assert_eq!(
            store.get(&id("crashed")).unwrap().unwrap().state,
            TaskState::Running
        );
        assert_eq!(store.events(&id("crashed")).unwrap().len(), 2);
        assert_eq!(store.recover_interrupted().unwrap(), 1);
        assert_eq!(store.get(&id("crashed")).unwrap().unwrap().version, 2);
        assert_eq!(
            store.events(&id("crashed")).unwrap().last().unwrap().state,
            TaskState::Interrupted
        );
    }

    #[test]
    fn event_failure_rolls_back_creation_transition_and_whole_recovery() {
        let mut store = SqliteTaskStore::open(":memory:").unwrap();
        let a = id("a");
        let b = id("b");
        store.create(&a).unwrap();
        store.create(&b).unwrap();
        store.connection.execute_batch("CREATE TRIGGER fail_events BEFORE INSERT ON task_events BEGIN SELECT RAISE(ABORT, 'injected failure'); END;").unwrap();
        assert!(store.create(&id("new")).is_err());
        assert!(store.get(&id("new")).unwrap().is_none());
        assert!(store.transition(&a, 0, TaskState::Running).is_err());
        assert_eq!(store.get(&a).unwrap().unwrap().version, 0);
        assert_eq!(store.events(&a).unwrap().len(), 1);
        store
            .connection
            .execute_batch("DROP TRIGGER fail_events;")
            .unwrap();
        store.transition(&a, 0, TaskState::Running).unwrap();
        store.transition(&b, 0, TaskState::Running).unwrap();
        store.connection.execute_batch("CREATE TRIGGER fail_second_recovery BEFORE INSERT ON task_events WHEN NEW.task_id = 'b' AND NEW.state = 'interrupted' BEGIN SELECT RAISE(ABORT, 'injected failure'); END;").unwrap();
        assert!(store.recover_interrupted().is_err());
        for task in [&a, &b] {
            assert_eq!(store.get(task).unwrap().unwrap().state, TaskState::Running);
            assert_eq!(store.events(task).unwrap().len(), 2);
        }
    }

    #[test]
    fn reopen_preserves_running_until_exclusive_explicit_recovery() {
        let db = TestDatabase::new();
        let task = id("restart");
        {
            let mut store = db.open();
            store.create(&task).unwrap();
            store.transition(&task, 0, TaskState::Running).unwrap();
            store.create(&id("queued")).unwrap();
        }
        let mut reopened = db.open();
        assert_eq!(
            reopened.get(&task).unwrap().unwrap().state,
            TaskState::Running
        );
        assert_eq!(reopened.recover_interrupted().unwrap(), 1);
        assert_eq!(reopened.recover_interrupted().unwrap(), 0);
        drop(reopened);
        let mut reopened = db.open();
        assert_eq!(
            reopened.get(&task).unwrap().unwrap(),
            TaskRecord {
                id: task.clone(),
                state: TaskState::Interrupted,
                version: 2
            }
        );
        assert_eq!(reopened.events(&task).unwrap().len(), 3);
        assert_eq!(
            reopened.get(&id("queued")).unwrap().unwrap().state,
            TaskState::Queued
        );
    }

    #[test]
    fn migration_failure_rolls_back_tables_and_schema_version() {
        let db = TestDatabase::new();
        {
            let connection = Connection::open(&db.0).unwrap();
            connection
                .execute_batch("CREATE TABLE task_events(existing INTEGER);")
                .unwrap();
        }
        assert!(SqliteTaskStore::open(&db.0).is_err());
        let connection = Connection::open(&db.0).unwrap();
        let version: i64 = connection
            .pragma_query_value(None, "user_version", |r| r.get(0))
            .unwrap();
        assert_eq!(version, 0);
        let task_tables: i64 = connection
            .query_row(
                "SELECT count(*) FROM sqlite_master WHERE name='tasks'",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(task_tables, 0);
    }

    #[test]
    fn future_schema_is_rejected_without_migration() {
        let db = TestDatabase::new();
        {
            let connection = Connection::open(&db.0).unwrap();
            connection
                .execute_batch("PRAGMA user_version = 2;")
                .unwrap();
        }
        assert!(matches!(
            SqliteTaskStore::open(&db.0),
            Err(TaskError::Storage(_))
        ));
        let connection = Connection::open(&db.0).unwrap();
        assert_eq!(
            connection
                .pragma_query_value(None, "user_version", |r| r.get::<_, i64>(0))
                .unwrap(),
            2
        );
        let tables: i64 = connection
            .query_row(
                "SELECT count(*) FROM sqlite_master WHERE type='table'",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(tables, 0);
    }
}
