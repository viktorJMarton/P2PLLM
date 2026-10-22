# Independent workflow, documentation and environment-tool review

Reviewer: /root/product_review. Run RUN-20261022-INDEPENDENT-REVIEW.
Uncommitted source, baseline 341be683d1da785fac2d9ad0e2b75b22e396f2ca.
This review also covers the WORK-0012 helper consumed by the audited workflow.
Final source identity/commit confirmation pending.

## Findings (initial snapshot)

1. **Blocking clean-bootstrap defect, open:** tools/dev_env.py install_zip
   strips an archive's root and moves it into `jdk-<version>`, yielding
   `jdk-<version>/bin/java.exe`. environment instead searches
   `jdk-<version>/*/bin/java.exe`. A fresh installation cannot activate its own
   installed JDK. Existing manually extracted cache layout can conceal the defect.
   Fix both layout handling and a fresh synthetic-archive activation regression.
   Sent directly to primary during review; no code edited by reviewer.
2. **Medium reproducibility defect, open:** doctor accepts any successful
   `cargo ndk --version`, while configuration lacks an expected cargo-ndk version.
   Exact expected version must be pinned/compared rather than inferred from
   exit zero. Java/javac output is recorded but also not compared to expected
   version. Validate expected tool versions and describe trusted-cache assumptions.
3. **Coverage improvements requested, not a false-pass bypass observed:**
   add tests for CRLF canonical receipts, self/duplicate/missing receipts and
   malformed questions. Current validator does report bad receipts as failures,
   although it advances the cadence marker regardless; only valid complete
   meeting structure should qualify for cadence reset.

## Observed review and checks

Read tools/validate_agent_flow.py, tests/test_agent_flow.py, tools/dev_env.py,
config/development-windows.json, source_inventory canonicalization helper,
root policy/meeting procedure, current role/template crosslinks and relevant
WORK-0002/3/4/9/10/11 evidence and briefs. Requirements/gates were not silently
relaxed by host-only stage dependencies. Historical WORK-0009 failed and passing
results remain explicit; no new-policy meeting was fabricated retroactively.

Direct reviewer command on Windows/Python 3.12.0:
`C:/Users/Viktor/AppData/Local/Programs/Python/Python312/python.exe -m unittest discover -s tests -p test_agent_flow.py -v`
exited 0; 4 tests passed. This does not validate semantic understanding or prove
that unlogged work never happened. Prefix receipts use utf8-lf-v1 bytes and are
compatible with append-only journals and checkout newline conversion by design;
behavioral newline regression requested above.

No network/bootstrap install performed by reviewer. Primary's WORK-0012 evidence
records actual compileDebugKotlin exit 0 in 3m28s on the unchanged Kotlin source;
doctor/bootstrap, native APK, emulator and physical-device checks are distinct.

Pending: primary fixes, associated tests, final frozen full workflow/docs checks
and independent exact-commit confirmation. This initial review is not acceptance.

## Fix recheck (second snapshot)

Finding 1 **resolved by source and direct test execution**: activation recognizes
the clean direct `bin/java.exe` layout and earlier nested layout, rejecting
ambiguity. Fresh synthetic ZIP installation-to-activation regression passes.

Finding 3 **resolved for requested scope**: invalid meeting structure no longer
resets cadence; CRLF conversion, self/duplicate/unresolved peer receipts and
persona declaration checks now have regressions. Validator remains structural.

Finding 2 **partly fixed, still open**: configuration now pins cargo-ndk and Rust;
doctor records expected values and rejects unrelated versions. However substring
matching still accepts near versions (e.g., expected 3.5.4 matches 13.5.4 or
3.5.40); same defect affects provision_rust's cargo-ndk check. Requested exact
version token matching and regression with expected SDK fixture files present.

Reviewer independently reran both suites on Windows/Python3.12: test_dev_env.py
5 passed/exit0; test_agent_flow.py 7 passed/exit0. No bootstrap/network installed.
Primary persona declaration read in role/index and appended to own journal:
pr-review with secondary security lens; no independent-review authority reset.

## Exact-version fix recheck (third snapshot)

Finding 2 **resolved**: shared matches_version requires whole version-token
boundaries and excludes prerelease suffixes; doctor and provision_rust use it.
Configuration pins the expected versions. The new SDK-complete doctor fixture
accepts exact 3.5.4 and rejects 13.5.4, 3.5.40 and 3.5.4-beta; missing files cannot
mask the version decision in that regression.

Reviewer independently reran `Python312/python.exe -m unittest discover -s tests
-p test_dev_env.py -v`: exit0, 6 tests pass. No remaining blocking source finding
within reviewed workflow/environment-tool scope. Final combined checks and
exact committed-source binding remain pending; this is not release approval.

Reviewed exact-byte SHA-256 for third snapshot:

| Path | SHA-256 |
| --- | --- |
| tools/dev_env.py | CA1D66F6644C88DEB131498BE9A82B0F82B2B35D661F38E83416036C0645F928 |
| tests/test_dev_env.py | A9777A21BCE3DF8F70F7C1E105778CABD9A2B00C9ADC53AAAA3252A4F423F5E5 |
| tools/validate_agent_flow.py | E64411221A1596281528AE95C405A95BFF85BF9D67CBD90BE8EC94E1AC10677D |
| tests/test_agent_flow.py | 17CF3532C972B2F0FAE64721ACBEC3B187EB84D6FCCE36F0102A66CBB963DE34 |
| config/development-windows.json | CA4324DDF82BEDBE3011A0AD23BECF60C91CCA38E2A994865B8C1F665E5986B2 |
