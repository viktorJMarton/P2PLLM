# Runner and behavioral-test handoff

- work_id: WORK-0009
- run_id: run-20261022-workflow-01
- role: testing / tooling implementer
- recipient_role: orchestrator, independent reviewer
- status: verified locally; independent review pending
- source_revision: uncommitted changes on 3dc5d2b1c4f03ac7ea90acbbdaf997e2ed213edd

## Inputs read
AGENTS.md; PRODUCT.md; TECHNOLOGY.md; docs/security/threat-model.md;
docs/architecture/overview.md; work/INDEX.md; this work brief;
agents/testing.md; tests/conformance-matrix.md; templates/handoff.md.

## Observed result
Implemented standard-library Python profile runner and 18 behavioral tests.
The runner records UTC times, platform/Python, exact argv, command exit/status,
HEAD and dirty state captured before creating its output. Shared source_inventory
produces canonical UTF-8/LF source fingerprints before and after checks; changed
source or HEAD fails the run. Commands run sequentially with shell=False and
bounded timeouts, stopping on the first nonpassing result; remaining checks are
explicitly not_run. No raw stdout, stderr or environment
variables enter reports. Configured argv must never contain secrets.

Exit codes: passed=0, failed=1, unavailable=2. Missing executable, absent Git
provenance, declared unavailability and empty checks cannot pass. A nonzero
command exit (including a missing pinned toolchain reported by its launcher) is
a failure. Later unavailability cannot hide failure. Required missing/unsafe
artifacts fail even when no bundle is requested.

ZIP creation is limited to passed runs, report.json and explicitly allowlisted
regular files. manifest.json hashes the bytes actually archived. Relative path
traversal, outside-repository paths, symlinks/junctions, duplicate artifacts,
artifact/report overlap and existing output directories are rejected. Existing
bundle collisions fail without deleting or overwriting the existing file.

## Changed paths
- tools/run_checks.py
- tests/test_run_checks.py
- work/WORK-0009-department-workflows/handoff-runner.md

## Verification
Windows host; Python 3.12.0; sanitized temporary Git repositories and synthetic
files/commands only. Command:

```powershell
& 'C:/Users/Viktor/AppData/Local/Programs/Python/Python312/python.exe' -m unittest discover -s tests -p test_run_checks.py -v
```

Exit 0: 18 tests discovered, 17 passed, 1 skipped. Windows symlink creation is
blocked by privilege 1314; the separate Windows junction escape test passed.
The skipped ordinary-symlink test must run on Linux CI. Failure, timeout,
unavailability, failure precedence, dirty/clean/missing provenance, unsafe paths,
missing artifacts, selective ZIP contents, SHA-256 integrity, source mutation,
descendant cleanup on timeout and collisions were
exercised. These results establish tooling behavior, not product/privacy/device
conformance. Parent owns persistent aggregate evidence and manifest refresh.

## Open risks / blockers
No Unix or Android execution was performed by this agent. Parent must run the
real configured profiles after updating the source manifest. Tooling trusts the
checked-in profile commands and the local workspace owner; path checks do not
provide an OS sandbox against hostile concurrent filesystem changes. Windows
uses kill-on-close Job Objects through standard-library ctypes, and POSIX uses
dedicated process groups. Windows taskkill was attempted during development but
returned Access denied under this host sandbox; this was a real failing test,
then corrected with Job Object cleanup. The final timeout descendant regression
passed. The implementation assumes trusted build commands and does not claim
containment against deliberately escaping child processes.

No signing, upload, installation, global Git configuration or remote writes.
No implementation commit exists; latest-commit independent review remains pending.

## Next action
Orchestrator reviews config compatibility, refreshes package manifest, executes
real profiles and requests independent review of the complete source snapshot.
