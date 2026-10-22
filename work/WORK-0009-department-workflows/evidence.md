# WORK-0009 evidence

Run: run-20261022-workflow-01. Base: 3dc5d2b, implementation uncommitted.
Environment: Windows, PowerShell; Python 3.12.0 via explicit Python312 path.
Observed checks and independent review will be recorded here after execution.

## Local observed results before implementation commit

All commands use `C:/Users/Viktor/AppData/Local/Programs/Python/Python312/python.exe`
as `python` below. Environment: Windows 11 10.0.26200, Python 3.12.0.

| Command | Exit | Observation |
| --- | ---: | --- |
| `python -m unittest discover -s tests -p test_*.py -v` | 0 | Independent review: 20 tests, 19 passed, 1 symlink privilege skip; junction and descendant cleanup tests pass |
| `python tools/run_checks.py --profile workflow --work-id WORK-0009 --run-id local-workflow-001 --bundle` | 1 | Test subprocess passed, but concurrent review-file update changed source fingerprint; no success bundle, correctly rejected unstable source |
| `python tools/run_checks.py --profile workflow --work-id WORK-0009 --run-id local-workflow-002 --bundle` | 0 | Frozen source, 20 tests / 1 skip; passed report and ZIP created |
| `python tools/run_checks.py --profile storage --work-id WORK-0009 --run-id local-unavailable-002 --bundle` | 2 | Unavailable as declared; correct HEAD and dirty state, stable source; no ZIP |
| `python tools/run_checks.py --profile rust --work-id WORK-0009 --run-id local-rust-001` | 1 | Installed Rust 1.88.0 missing; first command failed, remaining commands not_run; no toolchain install attempted |

The first real-root probes revealed null Git provenance because a Windows
backslash safe.directory value was not recognized. Corrected to as_posix();
local-unavailable-002 and local-workflow-002 include the correct base HEAD and
dirty:true. local-rust-001 predates that correction and is failure evidence only.

Reports and bundle: `.artifacts/checks/WORK-0009/<run>/<profile>/` (Git-ignored).
Only sanitized reports and explicitly configured artifacts are packaged.
Independent findings, resolutions and reviewed hashes: [review.md](review.md).
Runner and documentation handoffs are alongside this file. No Linux CI, Android
build/device, storage implementation or privacy capability was verified.
