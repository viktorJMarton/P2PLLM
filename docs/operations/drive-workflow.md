# Drive workflow for Codex CLI

The CLI rclone route remains design-only and OAuth is not configured there. The connected Google Drive plugin is used for owner-authorized versioned APK delivery (WORK-0014/0015 receipts); this connector access does not imply CLI OAuth access or a release approval.

Git owns active source history and review. Drive stores immutable source snapshots, documentation bundles, experiments, releases and incoming material. Never sync the active .git directory or credentials. No unattended two-way bisync or deletion mirroring. Fetch to staging, verify manifest, inspect diff, then normal Git review.

Snapshots include snapshot ID/time, commit, dirty flag and patch where applicable, file hashes and included work IDs. Use allowlisted export paths; exclude secrets, raw user content, runtime DBs and model keys. Model weights are not included by default; honor licenses and size policies.

Future commands: just drive-status / drive-publish WORK-ID / drive-fetch SNAPSHOT-ID / drive-verify SNAPSHOT-ID. Snapshot publication must not silently overwrite an existing ID. Root folder selection is not OAuth authorization scoping; rclone root_folder_id is an operational boundary only.

Original target: https://drive.google.com/drive/folders/1WJOZ6KhFsSS7ZvLpR8HGO3QVcwSbrypb . Current planning package is published as a dated versioned child folder and archive.
