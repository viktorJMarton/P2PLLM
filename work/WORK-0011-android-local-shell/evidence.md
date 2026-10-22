# WORK-0011 evidence

Run run-20261022-ui-01; implementation/checks in progress.
Android SDK/device not yet established. Do not claim a built APK without evidence.

## Observed execution and limits

Command: Python 3.12.0 `tools/run_checks.py --profile android --work-id WORK-0011
--run-id android-local-001 --bundle`, Windows 11 x86_64. Exit 1.
Installed Rust 1.88.0 preflight passed; Gradle lint launch exited 9009 because
JAVA_HOME is unset and java is absent from PATH. JVM tests/APK build were not_run;
no bundle was created. Android SDK/NDK and physical device are also not provisioned
or verified. Report: `.artifacts/checks/WORK-0011/android-local-001/android/report.json`.

Source includes five destinations, saved navigation, scroll/touch semantics,
off-main actual UniFFI status reads and lifecycle teardown. BridgeStatus is
unchanged and still reports default capability state, not the new CLI ledger.
No fake models, metrics or network controls are enabled. This is source delivery,
not a successful Android compile or real-device result.

Independent reviewer inspected early frozen UI source and found no blocking
source issue in those messages; final review/commit confirmation was interrupted
by the agent usage limit. It remains pending. No full WORK-0007 completion claim.

## Superseding current evidence, 2026-10-22

Agents resumed and wrote actual peer-journal questions/responses and independent
source reports. See review.md and work/agent-journals/{android-shell,product-review}.md.
WORK-0012 resolved Java/SDK provisioning and records Kotlin compile exit0 in3m28s
on unchanged source, native ARM64 bridge release build exit0 in2m08s and
assembleDebug exit0 in1m51s. This supersedes the missing-Java blocker for build
acceptance; the historical failed profile remains unchanged. Device/emulator
lifecycle, native bridge execution and full WORK-0007 network behavior are not
established by this APK build. Final commit/report confirmation follows.

## Final Android profile

Windows/JDK17/SDK35, `python tools/dev_env.py check --profile android --work-id
WORK-0011 --run-id push-final-002 --bundle`: exit0; lintDebug passed, JVM task
NO-SOURCE (no tests), ARM64 native bridge and assembleDebug passed. Report/bundle:
.artifacts/checks/WORK-0011/push-final-002/android/. First push-final-001 failed
on sandbox C:/.android access, retained; elevated002 succeeded.
APK9329531 bytes, SHA256e81af76449eda49a75229472128b3a310be11eacd734fd4227f287943b629bc1.
ZIP native libraries only arm64-v8a: Rust bridge, JNA and androidx graphics.
This supersedes the mixed-ABI artifact; no device/runtime acceptance claimed.
