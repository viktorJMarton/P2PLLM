//! Cooperative lifecycle ownership shared by CLI and Android composition roots.
//! Raw adapter callers must honor this contract; hardlink/replaced aliases are
//! unsupported. Keep the sibling lock file to avoid inode replacement races.

use fs2::FileExt;
use std::fs::{File, OpenOptions};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LeaseError {
    Busy,
    Unavailable,
}

impl std::fmt::Display for LeaseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self {
            Self::Busy => "Diagnostic database is in use; stop other owners before recovery",
            Self::Unavailable => "Diagnostic database ownership is unavailable",
        })
    }
}

impl std::error::Error for LeaseError {}

pub fn canonical_database(database: impl AsRef<Path>) -> Result<PathBuf, LeaseError> {
    let path = database.as_ref();
    if path.as_os_str().is_empty() || path.file_name().is_none() || path.is_dir() {
        return Err(LeaseError::Unavailable);
    }
    if path.exists() {
        path.canonicalize().map_err(|_| LeaseError::Unavailable)
    } else {
        let parent = path
            .parent()
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or(Path::new("."));
        parent
            .canonicalize()
            .map(|directory| directory.join(path.file_name().expect("checked file name")))
            .map_err(|_| LeaseError::Unavailable)
    }
}

pub struct DatabaseLease {
    pub database: PathBuf,
    _lock: File,
}

impl DatabaseLease {
    pub fn acquire(database: impl AsRef<Path>) -> Result<Self, LeaseError> {
        let canonical = canonical_database(database)?;
        let mut lock_name = canonical.as_os_str().to_os_string();
        lock_name.push(".owner.lock");
        let lock = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(PathBuf::from(lock_name))
            .map_err(|_| LeaseError::Unavailable)?;
        lock.try_lock_exclusive().map_err(|error| {
            if error.raw_os_error() == fs2::lock_contended_error().raw_os_error() {
                LeaseError::Busy
            } else {
                LeaseError::Unavailable
            }
        })?;
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
    fn lease_aliases_reject_concurrent_owner_and_release_on_drop() {
        let directory = std::env::temp_dir().join(format!(
            "p2p-shared-lease-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&directory).unwrap();
        let path = directory.join("node.db");
        let lease = DatabaseLease::acquire(&path).unwrap();
        assert!(matches!(
            DatabaseLease::acquire(directory.join(".").join("node.db")),
            Err(LeaseError::Busy)
        ));
        assert!(!path.exists());
        drop(lease);
        let lease = DatabaseLease::acquire(&path).unwrap();
        std::fs::write(&lease.database, b"").unwrap();
        assert!(matches!(
            DatabaseLease::acquire(&path),
            Err(LeaseError::Busy)
        ));
        drop(lease);
        assert!(DatabaseLease::acquire("").is_err());
        assert!(DatabaseLease::acquire(&directory).is_err());
        std::fs::remove_file(&path).unwrap();
        std::fs::remove_file(directory.join("node.db.owner.lock")).unwrap();
        std::fs::remove_dir(directory).unwrap();
    }
}
