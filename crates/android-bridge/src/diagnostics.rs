//! Process-owned, bounded local diagnostic composition root. No AI work.

use p2p_node_core::tasks::{
    finish_local_diagnostic, start_local_diagnostic, TaskError, TaskId, TaskRecord, TaskState,
    TaskStore,
};
use p2p_storage_sqlite::{
    lease::{canonical_database, DatabaseLease, LeaseError},
    SqliteTaskStore, MAX_DIAGNOSTIC_OFFSET, MAX_DIAGNOSTIC_PAGE_SIZE,
};
use std::{
    collections::HashMap,
    path::{Path, PathBuf},
    sync::{Arc, Mutex, OnceLock, TryLockError},
};

const MAX_DATABASES: usize = 16;
const SCHEMA_VERSION: u32 = 1;

#[derive(Debug, Clone, Copy, PartialEq, Eq, uniffi::Error)]
pub enum DiagnosticError {
    InvalidRequest,
    Busy,
    StorageUnavailable,
    RecoveryRequired,
    Internal,
}

impl std::fmt::Display for DiagnosticError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self {
            Self::InvalidRequest => "Invalid local diagnostic request",
            Self::Busy => "Local diagnostics busy",
            Self::StorageUnavailable => "Local diagnostic storage unavailable",
            Self::RecoveryRequired => "Local diagnostic recovery required",
            Self::Internal => "Local diagnostic internal failure",
        })
    }
}
impl std::error::Error for DiagnosticError {}

#[derive(Debug, Clone, Copy, PartialEq, Eq, uniffi::Enum)]
pub enum DiagnosticState {
    Queued,
    Running,
    Succeeded,
    Failed,
    Cancelled,
    Interrupted,
}

#[derive(Debug, Clone, PartialEq, Eq, uniffi::Record)]
pub struct DiagnosticRecord {
    pub schema_version: u32,
    pub request_id: String,
    pub state: DiagnosticState,
    pub version: u64,
}

impl From<TaskRecord> for DiagnosticRecord {
    fn from(record: TaskRecord) -> Self {
        Self {
            schema_version: SCHEMA_VERSION,
            request_id: record.id.as_str().into(),
            state: match record.state {
                TaskState::Queued => DiagnosticState::Queued,
                TaskState::Running => DiagnosticState::Running,
                TaskState::Succeeded => DiagnosticState::Succeeded,
                TaskState::Failed => DiagnosticState::Failed,
                TaskState::Cancelled => DiagnosticState::Cancelled,
                TaskState::Interrupted => DiagnosticState::Interrupted,
            },
            version: record.version,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, uniffi::Record)]
pub struct DiagnosticPage {
    pub schema_version: u32,
    pub records: Vec<DiagnosticRecord>,
    pub offset: u32,
    pub next_offset: Option<u32>,
}

struct OwnedStore {
    store: SqliteTaskStore,
    _lease: DatabaseLease,
}

#[derive(uniffi::Object)]
pub struct LocalDiagnostics {
    owner: Mutex<OwnedStore>,
}

fn lock_error<T>(error: TryLockError<T>) -> DiagnosticError {
    match error {
        TryLockError::WouldBlock => DiagnosticError::Busy,
        TryLockError::Poisoned(_) => DiagnosticError::Internal,
    }
}

fn task_error(error: TaskError) -> DiagnosticError {
    match error {
        TaskError::InvalidId => DiagnosticError::InvalidRequest,
        TaskError::InvalidTransition {
            from: TaskState::Running,
            to: TaskState::Running,
        } => DiagnosticError::RecoveryRequired,
        TaskError::Storage(_) => DiagnosticError::StorageUnavailable,
        TaskError::VersionConflict { .. } => DiagnosticError::Busy,
        _ => DiagnosticError::Internal,
    }
}

impl LocalDiagnostics {
    fn initialize(path: &Path) -> Result<Self, DiagnosticError> {
        let lease = DatabaseLease::acquire(path).map_err(|error| match error {
            LeaseError::Busy => DiagnosticError::Busy,
            LeaseError::Unavailable => DiagnosticError::StorageUnavailable,
        })?;
        let mut store = SqliteTaskStore::open(&lease.database).map_err(task_error)?;
        // This new exclusive owner has not exposed an object or started work.
        // Existing process handles never call initialize again for this path.
        store
            .recover_interrupted()
            .map_err(|_| DiagnosticError::RecoveryRequired)?;
        Ok(Self {
            owner: Mutex::new(OwnedStore {
                store,
                _lease: lease,
            }),
        })
    }

    fn run_inner(
        &self,
        request_id: String,
        after_running: impl FnOnce(),
    ) -> Result<DiagnosticRecord, DiagnosticError> {
        let id = TaskId::new(request_id).map_err(task_error)?;
        let mut owner = self.owner.try_lock().map_err(lock_error)?;
        let record = start_local_diagnostic(&mut owner.store, &id).map_err(task_error)?;
        let result = if record.state == TaskState::Running {
            // Production always passes a no-op. Tests can pause at the actual
            // persisted Running boundary without exposing a hook over UniFFI.
            after_running();
            finish_local_diagnostic(&mut owner.store, &record).map_err(task_error)?
        } else {
            record
        };
        Ok(result.into())
    }

    #[cfg(test)]
    fn run_with_test_hook(
        &self,
        id: String,
        after_running: impl FnOnce(),
    ) -> Result<DiagnosticRecord, DiagnosticError> {
        self.run_inner(id, after_running)
    }
}

#[uniffi::export]
impl LocalDiagnostics {
    pub fn run(&self, request_id: String) -> Result<DiagnosticRecord, DiagnosticError> {
        self.run_inner(request_id, || {})
    }

    pub fn list(&self, limit: u32, offset: u32) -> Result<DiagnosticPage, DiagnosticError> {
        if !(1..=MAX_DIAGNOSTIC_PAGE_SIZE).contains(&limit) || offset > MAX_DIAGNOSTIC_OFFSET {
            return Err(DiagnosticError::InvalidRequest);
        }
        let owner = self.owner.try_lock().map_err(lock_error)?;
        let page = owner.store.list_page(limit, offset).map_err(task_error)?;
        Ok(DiagnosticPage {
            schema_version: SCHEMA_VERSION,
            records: page.records.into_iter().map(Into::into).collect(),
            offset,
            next_offset: page.next_offset,
        })
    }
}

#[derive(Default)]
struct Registry {
    // Strong references deliberately live until process exit, bounded below.
    owners: HashMap<PathBuf, Arc<LocalDiagnostics>>,
}

impl Registry {
    fn open(&mut self, canonical: PathBuf) -> Result<Arc<LocalDiagnostics>, DiagnosticError> {
        if let Some(existing) = self.owners.get(&canonical) {
            return Ok(existing.clone());
        }
        if self.owners.len() >= MAX_DATABASES {
            return Err(DiagnosticError::Busy);
        }
        let owner = Arc::new(LocalDiagnostics::initialize(&canonical)?);
        self.owners.insert(canonical, owner.clone());
        Ok(owner)
    }
}

#[uniffi::export]
pub fn open_local_diagnostics(
    database_path: String,
) -> Result<Arc<LocalDiagnostics>, DiagnosticError> {
    if database_path.len() > 4096
        || database_path.contains('\0')
        || !Path::new(&database_path).is_absolute()
    {
        return Err(DiagnosticError::InvalidRequest);
    }
    let canonical =
        canonical_database(&database_path).map_err(|_| DiagnosticError::StorageUnavailable)?;
    static REGISTRY: OnceLock<Mutex<Registry>> = OnceLock::new();
    REGISTRY
        .get_or_init(|| Mutex::new(Registry::default()))
        .try_lock()
        .map_err(lock_error)?
        .open(canonical)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        process::{Child, Command, Stdio},
        time::{Duration, Instant},
    };

    struct TestDirectory(PathBuf);
    impl TestDirectory {
        fn new() -> Self {
            let directory = std::env::temp_dir().join(format!(
                "p2p-bridge-diag-{}-{}",
                std::process::id(),
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos()
            ));
            std::fs::create_dir(&directory).unwrap();
            Self(directory)
        }
        fn database(&self) -> PathBuf {
            self.0.join("diagnostic.sqlite3")
        }
        fn canonical(&self) -> PathBuf {
            canonical_database(self.database()).unwrap()
        }
    }
    impl Drop for TestDirectory {
        fn drop(&mut self) {
            // Unique known test directory; remove only test-created regular files.
            if let Ok(entries) = std::fs::read_dir(&self.0) {
                for entry in entries.flatten() {
                    if entry.file_type().is_ok_and(|kind| kind.is_file()) {
                        let _ = std::fs::remove_file(entry.path());
                    }
                }
            }
            let _ = std::fs::remove_dir(&self.0);
        }
    }

    #[test]
    fn actual_diagnostic_is_idempotent_and_pages_are_bounded_ordered() {
        let directory = TestDirectory::new();
        let mut registry = Registry::default();
        let runtime = registry.open(directory.canonical()).unwrap();
        let first = runtime.run("job-b".into()).unwrap();
        assert_eq!(first.state, DiagnosticState::Succeeded);
        assert_eq!(first.version, 2);
        assert_eq!(runtime.run("job-b".into()).unwrap(), first);
        runtime.run("job-a".into()).unwrap();
        runtime.run("job-c".into()).unwrap();
        let page = runtime.list(2, 0).unwrap();
        assert_eq!(
            page.records
                .iter()
                .map(|record| record.request_id.as_str())
                .collect::<Vec<_>>(),
            vec!["job-a", "job-b"]
        );
        assert_eq!(page.next_offset, Some(2));
        let last = runtime.list(2, 2).unwrap();
        assert_eq!(last.records[0].request_id, "job-c");
        assert_eq!(last.next_offset, None);
        assert!(runtime.list(50, 10_000).unwrap().records.is_empty());
        for (limit, offset) in [(0, 0), (51, 0), (1, 10_001), (u32::MAX, u32::MAX)] {
            assert_eq!(
                runtime.list(limit, offset),
                Err(DiagnosticError::InvalidRequest)
            );
        }
        assert_eq!(
            runtime.run("bad/id".into()),
            Err(DiagnosticError::InvalidRequest)
        );
        let owner = runtime.owner.try_lock().unwrap();
        assert_eq!(
            owner
                .store
                .events(&TaskId::new("job-b").unwrap())
                .unwrap()
                .len(),
            3
        );
        assert_eq!(
            owner
                .store
                .events(&TaskId::new("job-a").unwrap())
                .unwrap()
                .len(),
            3
        );
    }

    #[test]
    fn activity_reopen_while_running_reuses_owner_without_recovery() {
        let directory = TestDirectory::new();
        let registry = Arc::new(Mutex::new(Registry::default()));
        let runtime = registry
            .lock()
            .unwrap()
            .open(directory.canonical())
            .unwrap();
        let (started_tx, started_rx) = std::sync::mpsc::channel();
        let (finish_tx, finish_rx) = std::sync::mpsc::channel();
        let worker_runtime = runtime.clone();
        let worker = std::thread::spawn(move || {
            worker_runtime.run_with_test_hook("live".into(), || {
                started_tx.send(()).unwrap();
                finish_rx.recv_timeout(Duration::from_secs(10)).unwrap();
            })
        });
        started_rx.recv_timeout(Duration::from_secs(10)).unwrap();
        let reopened = registry
            .lock()
            .unwrap()
            .open(directory.canonical())
            .unwrap();
        assert!(Arc::ptr_eq(&runtime, &reopened));
        assert_eq!(reopened.run("other".into()), Err(DiagnosticError::Busy));
        assert_eq!(reopened.list(10, 0), Err(DiagnosticError::Busy));
        assert!(matches!(
            DatabaseLease::acquire(directory.database()),
            Err(LeaseError::Busy)
        ));
        finish_tx.send(()).unwrap();
        assert_eq!(
            worker.join().unwrap().unwrap().state,
            DiagnosticState::Succeeded
        );
        assert_eq!(reopened.list(10, 0).unwrap().records[0].version, 2);
        drop(runtime);
        drop(reopened);
        // Registry's strong owner outlives all Activity-style handles.
        assert!(matches!(
            DatabaseLease::acquire(directory.database()),
            Err(LeaseError::Busy)
        ));
        drop(registry);
        assert!(DatabaseLease::acquire(directory.database()).is_ok());
    }

    #[test]
    fn first_owner_recovers_running_once_and_preserves_terminal() {
        let directory = TestDirectory::new();
        let running = TaskId::new("abandoned").unwrap();
        {
            let mut store = SqliteTaskStore::open(directory.database()).unwrap();
            p2p_node_core::tasks::run_local_diagnostic(&mut store, &TaskId::new("done").unwrap())
                .unwrap();
            start_local_diagnostic(&mut store, &running).unwrap();
        }
        let mut registry = Registry::default();
        let runtime = registry.open(directory.canonical()).unwrap();
        let interrupted = runtime.run("abandoned".into()).unwrap();
        assert_eq!(interrupted.state, DiagnosticState::Interrupted);
        assert_eq!(interrupted.version, 2);
        assert_eq!(
            runtime.run("done".into()).unwrap().state,
            DiagnosticState::Succeeded
        );
        let reopened = registry.open(directory.canonical()).unwrap();
        assert!(Arc::ptr_eq(&runtime, &reopened));
        assert_eq!(reopened.run("abandoned".into()).unwrap(), interrupted);
        assert_eq!(
            runtime
                .owner
                .try_lock()
                .unwrap()
                .store
                .events(&running)
                .unwrap()
                .len(),
            3
        );
    }

    #[test]
    fn crash_child_waits_after_real_persisted_running() {
        let Some(database) = std::env::var_os("P2PLLM_DIAGNOSTIC_CRASH_DATABASE") else {
            return;
        };
        let ready = PathBuf::from(std::env::var_os("P2PLLM_DIAGNOSTIC_CRASH_READY").unwrap());
        let database = database.into_string().unwrap();
        let runtime = open_local_diagnostics(database.clone()).unwrap();
        runtime
            .run_with_test_hook("killed".into(), || {
                // Exercise the actual exported process registry while Running,
                // not merely a test-local owner map.
                let reopened = open_local_diagnostics(database.clone()).unwrap();
                assert!(Arc::ptr_eq(&runtime, &reopened));
                assert_eq!(reopened.list(10, 0), Err(DiagnosticError::Busy));
                std::fs::write(ready, b"running-committed").unwrap();
                loop {
                    std::thread::park();
                }
            })
            .unwrap();
    }

    struct KillOnDrop(Child);
    impl Drop for KillOnDrop {
        fn drop(&mut self) {
            let _ = self.0.kill();
            let _ = self.0.wait();
        }
    }

    #[test]
    fn killed_process_releases_lease_and_next_owner_recovers_persisted_running() {
        let directory = TestDirectory::new();
        let ready = directory.0.join("child.ready");
        let mut child = KillOnDrop(
            Command::new(std::env::current_exe().unwrap())
                .args([
                    "--exact",
                    "diagnostics::tests::crash_child_waits_after_real_persisted_running",
                    "--nocapture",
                ])
                .env("P2PLLM_DIAGNOSTIC_CRASH_DATABASE", directory.database())
                .env("P2PLLM_DIAGNOSTIC_CRASH_READY", &ready)
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn()
                .unwrap(),
        );
        let started = Instant::now();
        while !ready.exists() {
            assert!(
                started.elapsed() < Duration::from_secs(15),
                "child never reached Running hook"
            );
            assert!(
                child.0.try_wait().unwrap().is_none(),
                "child exited before Running hook"
            );
            std::thread::sleep(Duration::from_millis(10));
        }
        assert!(matches!(
            DatabaseLease::acquire(directory.database()),
            Err(LeaseError::Busy)
        ));
        child.0.kill().unwrap();
        assert!(!child.0.wait().unwrap().success());
        let mut registry = Registry::default();
        let runtime = registry.open(directory.canonical()).unwrap();
        let record = runtime.run("killed".into()).unwrap();
        assert_eq!(record.state, DiagnosticState::Interrupted);
        assert_eq!(record.version, 2);
        assert_eq!(
            runtime
                .owner
                .try_lock()
                .unwrap()
                .store
                .events(&TaskId::new("killed").unwrap())
                .unwrap()
                .len(),
            3
        );
    }

    #[test]
    fn registry_capacity_and_failures_have_stable_errors() {
        let directory = TestDirectory::new();
        let mut registry = Registry::default();
        for index in 0..MAX_DATABASES {
            let path = canonical_database(directory.0.join(format!("db-{index}"))).unwrap();
            registry.open(path).unwrap();
        }
        assert!(matches!(
            registry.open(canonical_database(directory.0.join("overflow")).unwrap()),
            Err(DiagnosticError::Busy)
        ));
        assert!(!directory.0.join("overflow").exists());
        assert!(!directory.0.join("overflow.owner.lock").exists());
        assert!(registry
            .open(canonical_database(directory.0.join("db-0")).unwrap())
            .is_ok());
        assert!(matches!(
            open_local_diagnostics(":memory:".into()),
            Err(DiagnosticError::InvalidRequest)
        ));
        assert!(matches!(
            open_local_diagnostics("bad\0path".into()),
            Err(DiagnosticError::InvalidRequest)
        ));
        let missing = directory.0.join("missing-parent").join("diagnostics.db");
        assert!(matches!(
            open_local_diagnostics(missing.to_string_lossy().into()),
            Err(DiagnosticError::StorageUnavailable)
        ));
        for error in [
            DiagnosticError::InvalidRequest,
            DiagnosticError::Busy,
            DiagnosticError::StorageUnavailable,
            DiagnosticError::RecoveryRequired,
            DiagnosticError::Internal,
        ] {
            assert!(!error.to_string().contains(directory.0.to_str().unwrap()));
        }
    }

    #[test]
    fn active_external_lease_blocks_initialization_then_abandoned_work_recovers() {
        let directory = TestDirectory::new();
        let lease = DatabaseLease::acquire(directory.database()).unwrap();
        let mut registry = Registry::default();
        assert!(matches!(
            registry.open(directory.canonical()),
            Err(DiagnosticError::Busy)
        ));
        assert!(registry.owners.is_empty());
        drop(lease);
        {
            let mut store = SqliteTaskStore::open(directory.database()).unwrap();
            let task = TaskId::new("orphan").unwrap();
            store.create(&task).unwrap();
            store.transition(&task, 0, TaskState::Running).unwrap();
        }
        let runtime = registry.open(directory.canonical()).unwrap();
        assert_eq!(
            runtime.list(10, 0).unwrap().records[0].state,
            DiagnosticState::Interrupted
        );
    }

    #[test]
    fn unreadable_store_and_unexpected_running_never_become_fake_success() {
        let directory = TestDirectory::new();
        std::fs::write(directory.database(), b"not a SQLite database").unwrap();
        let mut registry = Registry::default();
        assert!(matches!(
            registry.open(directory.canonical()),
            Err(DiagnosticError::StorageUnavailable)
        ));
        assert!(registry.owners.is_empty());
        std::fs::remove_file(directory.database()).unwrap();
        let runtime = registry.open(directory.canonical()).unwrap();
        {
            let mut owner = runtime.owner.try_lock().unwrap();
            start_local_diagnostic(
                &mut owner.store,
                &TaskId::new("unexpected-running").unwrap(),
            )
            .unwrap();
        }
        assert_eq!(
            runtime.run("unexpected-running".into()),
            Err(DiagnosticError::RecoveryRequired)
        );
        let reopened = registry.open(directory.canonical()).unwrap();
        assert_eq!(
            reopened.list(10, 0).unwrap().records[0].state,
            DiagnosticState::Running
        );
        assert_eq!(
            reopened.run("unexpected-running".into()),
            Err(DiagnosticError::RecoveryRequired)
        );
    }
}
