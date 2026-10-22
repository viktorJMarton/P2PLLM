# WORK-0009 independent review

Run ID: review-20261022-01. Reviewer: independent_review agent.
Base commit: 3dc5d2b1c4f03ac7ea90acbbdaf997e2ed213edd.
Source status: uncommitted; final snapshot review in progress.
Environment: Windows PowerShell; Python 3.12.0 at C:/Users/Viktor/AppData/Local/Programs/Python/Python312/python.exe.
Owned path: this report only. No implementation changes or shared journal edits.

## Initial observations

- Command: explicit Python312 `-m unittest discover -s tests -p test_*.py -v`.
  Exit 0: 18 tests, one skip because Windows symlink creation requires unavailable privilege (1314). Windows junction rejection passed.
- P1, tools/run_checks.py execute(): timeout terminated only the direct child.
  Reproduced with a Python parent spawning a finite child: child slept two seconds,
  then wrote a sanitized marker; parent slept 15 seconds and runner timed out at
  one second. Three seconds after timeout the marker existed. Descendants could
  mutate output after failed evidence. Sent to runner author; resolution pending.
- P2, config/check-profiles.json Rust/Android invocation: commands currently
  reach rustup shims/Gradle wrapper without a provisioned-toolchain preflight.
  rust-toolchain.toml selects 1.88.0; Gradle wrapper properties specify a download
  URL. This does not enforce the brief's exclusion of toolchain auto-install.
  No network/toolchain commands were executed for this finding. Root notified.

Final source hashes, final checks, and resolution status will be appended after
implementation stabilizes. Commit-bound independent review remains pending.

## Final source review and resolutions

Final review was performed against the uncommitted source snapshot below on
branch work/WORK-0009-workflows, base commit stated above.

- P1 resolved for the trusted build-command harness: Windows kill-on-close Job
  Objects and POSIX process groups replace direct-child-only timeout cleanup.
  The new descendant timeout test passed. This is not a malicious-process
  sandbox; Windows assignment happens after child launch.
- P2 resolved: Rust invokes explicit `rustup run 1.88.0`; Android checks that
  installed toolchain first. The brief and workflow accurately allow pinned
  dependency/Gradle-distribution restoration over the network on provisioned
  hosts. No toolchain/network build was run by this reviewer.
- Parent found and fixed Windows safe.directory slash syntax in git_provenance.
  Independent real-root probe now returns the correct base HEAD and dirty:true.
- No remaining blocking correctness finding in the reviewed scope. Profiles
  stop on the first nonpass, mark later commands not_run, fail changed-source
  snapshots, and bundle only passing reports plus declared files. Bundle hashes
  cover archived raw bytes. Source inventory normalization is separate.

## Final observed verification

- Explicit Python312 `-m unittest discover -s tests -p test_*.py -v`:
  exit 0; 20 tests, 19 passed and one skipped (symlink privilege 1314).
  Windows junction rejection and descendant cleanup passed.
- Sanitized Windows `.bat` fixture under a path containing spaces, with
  shell=False and arguments: exit /b 7 was recorded as failed/exit_code 7.
- Real-root storage profile, run review-unavailable-002, --bundle: process exit
  2, report unavailable, HEAD correct, dirty:true, source_before=source_after,
  no bundle. Evidence: .artifacts/checks/WORK-0009/review-unavailable-002/storage/report.json.
- No Rust/Android build, remote CI, Linux execution or physical-device test by
  this reviewer. Canonical CRLF/LF and binary-preservation tests passed on
  Windows; actual Linux runtime evidence remains unobserved here.

## Reviewed source SHA-256

These are raw file bytes, excluding logs, generated manifests, handoffs and this
review. This list identifies the reviewed changed implementation/docs snapshot;
commit-bound review is pending until the parent creates and supplies a commit.

```json
{
  ".github/workflows/ci.yml": "b4d710a656633000260de7a2d264783eacb80c109a0d0f4de74ab084906fc650",
  ".gitignore": "339fcc76d41e3d3f7b8509096574d448627a61d034abb1dbc5ecf4f8194f6deb",
  "AGENTS.md": "3cc17825f82ef253c2517dcb72de2cb953f2bf3c311446c6788e6468ea4dd18c",
  "BUILD.md": "930542f241318fc7b935e2093fa73ee9273fa104a63f5e46286e0c1cc751885b",
  "docs/operations/ci-review.md": "27f578415d1e9de5f695c4dfda3efb96aea68224fe15487f562e7822c0f405c6",
  "docs/operations/department-workflow.md": "ffac69c3e2a4db94fa3ff76f29345c3c6c1d535005e1cb2ea14027c3541818eb",
  "justfile": "745f2c05c725ce654a970b775a3a3dc16bcc79738218204ed610bea5d5e5d524",
  "config/check-profiles.json": "657a8e5a209c81b9092d8489bc78eff497ad5c9d8c8676660b6301bc7ed9c065",
  "templates/department-handoff.md": "fb78443864f1262665d5e1fb4caa12ad668d70718ada05cfb0d11d4218a4e1fe",
  "tools/run_checks.py": "585bf4d71705aafe0d347c290092bd9227d3562dc4b01dd2d4a60b4217958429",
  "tools/source_inventory.py": "42f33bf500a648d94e9f3ef4728937bf67d032ec326c057d49e565d2290d6863",
  "tools/update_manifest.py": "d2e5a473f8a6c08715756696bef250de44304a60666ab92bf9d544931d9595ea",
  "tools/validate_package.py": "99af8dedd518f8340e276c2ca8a4abe508773d622193d2cca5b6818c20495197",
  "tests/test_run_checks.py": "f88ddca4c12560e50e993e25ad1c11f2e4d3f34e1f1e50645a97646577efc525",
  "tests/test_source_inventory.py": "23d5ee48d06602abcefd2a048fe2472a7608fd6a748888bb04554303db92a2bc",
  "work/INDEX.md": "7dfc337fdb2ca82e9550aa013189e5790f7b8a7a9b27f7446e65c380453aa678",
  "work/WORK-0009-department-workflows/brief.md": "b86c297bdbc47a7a42d52f1293b108d1c5cfb5ac4c35ba2018296f153ba83a8b"
}
```
