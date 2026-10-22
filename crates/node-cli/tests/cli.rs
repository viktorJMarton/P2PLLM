//! Exercise the shipped executable across independent database opens.

use std::path::PathBuf;
use std::process::{Command, Output};

fn invoke(args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_p2p-node"))
        .args(args)
        .output()
        .unwrap()
}

struct TestDirectory(PathBuf);

impl TestDirectory {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "p2p-cli-test-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&path).unwrap();
        Self(path)
    }
}

impl Drop for TestDirectory {
    fn drop(&mut self) {
        // Only known files within this unique test directory; never recurse.
        for name in ["node.db", "node.db.owner.lock", "node.db-journal"] {
            let _ = std::fs::remove_file(self.0.join(name));
        }
        let _ = std::fs::remove_dir(&self.0);
    }
}

#[test]
fn completed_diagnostic_persists_across_processes_and_is_idempotent() {
    let directory = TestDirectory::new();
    let database = directory.0.join("node.db");
    let path = database.to_str().unwrap();
    let first = invoke(&["diagnostic", "run", path, "smoke-01"]);
    assert!(
        first.status.success(),
        "{}",
        String::from_utf8_lossy(&first.stderr)
    );
    assert!(String::from_utf8_lossy(&first.stdout).contains("\"state\":\"succeeded\""));
    let repeated = invoke(&["diagnostic", "run", path, "smoke-01"]);
    assert!(repeated.status.success());
    assert_eq!(first.stdout, repeated.stdout);
    let listed = invoke(&["jobs", "list", path]);
    assert!(listed.status.success());
    assert_eq!(
        String::from_utf8_lossy(&listed.stdout).trim(),
        format!("[{}]", String::from_utf8_lossy(&first.stdout).trim())
    );
    assert!(!invoke(&["jobs", "recover", path]).status.success());
    let recovered = invoke(&["jobs", "recover", path, "--offline"]);
    assert!(recovered.status.success());
    assert_eq!(
        String::from_utf8_lossy(&recovered.stdout).trim(),
        "{\"interrupted\":0}"
    );
}

#[test]
fn invalid_id_does_not_create_database_or_lock_file() {
    let directory = TestDirectory::new();
    let database = directory.0.join("node.db");
    assert!(
        !invoke(&["diagnostic", "run", database.to_str().unwrap(), "bad/id"])
            .status
            .success()
    );
    assert!(!database.exists());
    assert!(!directory.0.join("node.db.owner.lock").exists());
}

#[test]
fn status_retains_existing_machine_contract() {
    let status = invoke(&["status"]);
    assert!(status.status.success());
    assert_eq!(String::from_utf8_lossy(&status.stdout).trim(),
        "{\"schema_version\":1,\"network_enabled\":false,\"private_compute\":\"unavailable\",\"private_learning\":\"unavailable\"}");
}
