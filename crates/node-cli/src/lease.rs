//! Cooperative process ownership for the CLI's diagnostic database lifecycle.

use fs2::FileExt;
use p2p_node_core::tasks::TaskError;
use std::fs::{File, OpenOptions};
use std::path::{Path, PathBuf};

pub struct DatabaseLease {
    pub database: PathBuf,
    _lock: File,
}

impl DatabaseLease {
    pub fn acquire(database: &str) -> Result<Self, TaskError> {
        let path = Path::new(database);
        let canonical = if path.exists() {
            path.canonicalize()
        } else {
            let parent = path
                .parent()
                .filter(|p| !p.as_os_str().is_empty())
                .unwrap_or(Path::new("."));
            parent
                .canonicalize()
                .map(|directory| directory.join(path.file_name().unwrap_or_default()))
        }
        .map_err(|_| TaskError::Storage("Cannot resolve diagnostic database location".into()))?;
        let mut lock_name = canonical.as_os_str().to_os_string();
        lock_name.push(".owner.lock");
        let lock = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(PathBuf::from(lock_name))
            .map_err(|_| TaskError::Storage("Cannot open diagnostic ownership lock".into()))?;
        lock.try_lock_exclusive().map_err(|_| {
            TaskError::Storage(
                "Diagnostic database is in use; stop other owners before recovery".into(),
            )
        })?;
        // Keep the file and handle: deleting a lock file would permit inode races.
        Ok(Self {
            database: canonical,
            _lock: lock,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lease_rejects_concurrent_owner_and_releases_on_drop() {
        let name = format!(
            "p2p-lease-test-{}-{}.db",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        );
        let path = std::env::temp_dir().join(name);
        let lease = DatabaseLease::acquire(path.to_str().unwrap()).unwrap();
        assert!(DatabaseLease::acquire(path.to_str().unwrap()).is_err());
        drop(lease);
        drop(DatabaseLease::acquire(path.to_str().unwrap()).unwrap());
        let mut lock = path.into_os_string();
        lock.push(".owner.lock");
        std::fs::remove_file(PathBuf::from(lock)).unwrap();
    }
}
