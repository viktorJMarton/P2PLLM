# WORK-0015 integration journal

Owner primary, persona Accountable delivery coordinator; run
run-20261024-local-inference-01. Disjoint Android/native ownership in the shared
checkout; separate journals/handoffs. Parent9f33493; dedicated development branch
work/WORK-0015-offline-android-ai. Root counter continued27-35 with meetings28,
31,34; late meeting28 deviation is explicitly preserved in the primary journal.

Observed source implementation and actual A72 acceptance: [evidence](evidence.md),
[portable receipts](device-observations.json). Eight installed-app checks passed;
prior failed build/audit/answer attempts retained. No rewritten success claims.

Accepted shared decisions: positive request IDs close pre-entry cancellation;
worker-only native runner access; exact pinned assets verified off main thread;
debug APK bundles public model; measured nonthinking template suffix; distinct
pre/post-AGP-strip identities. Native and Android owners actually agreed; see
their journals and primary meetings. ADR-013 explicitly scopes the JNI exception.

Final checks/review/commit/push/Drive receipt pending until appended below.

## Actual source push and archival Drive handoff

Exact source630ef77bac1fe065fa17b88ad4b45735cf6217a0 independently bound by
nonauthor delivery_review: NO BLOCKER for bounded app slice. Actual push -u origin
work/WORK-0015-offline-android-ai exit0; ls-remote exit0 matched sourceSHA.
Final source docs offline-final-002 passed720 package checks plus journalpolicy;
Android offline-app-002 and workflow evidence remain as above. No source/APK
change follows this delivery metadata.

Whole APK upload failed HTTP413: connector104857600byte cap versus509885353B.
No CLI rclone/Drive desktop is configured. Separate local Drive OAuth choice was
asked; no answer or consent is inferred. WORK-0015 stays in_progress/delivery
pending; this is not a successful full sprint closure or a single-file upload.

Actual [Drive archive](https://drive.google.com/drive/folders/1m56z-ZOaqFpRbRzkJooa3OuvU1JXfFhB)
contains6 bytewise parts, Join-APK.cmd, public instructions, model/build/test
metadata, checksums and DELIVERY.json (14files). Parts are not individually
installable. Actual Windows CMD reconstruction exit0 yielded509885353B and exact
original APK SHA; an independent reviewer rehashed allparts/concatenation.
Readback verified13files' names/sizes/parents, then DELIVERY.json metadata and
14file folder listing. Connector exposes no remote checksum, so remote byte
integrity is not independently verified. [Delivery receipt](delivery.json).

Local original .artifacts/delivery/WORK-0015/630ef77/P2PLLM-v0.3.0-code3-arm64-debug-630ef77.apk
remains available and the app is already installed/tested on A72. Next owner
primary resumes single-file Drive transfer only after local authentication;
continue WORK-0002 quality/backend work independently. Metadata follow-up final
commit/review/push is pending until actually executed, without a release/default
branch merge. Full numerical/backend/privacy/thermal gates remain open.
