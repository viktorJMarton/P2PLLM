#!/usr/bin/env python3
"""Refresh the source inventory after intentional repository changes.

The original handoff remains recoverable from the first Git commit.
"""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
manifest_path = root / "MANIFEST.json"
manifest = json.loads(manifest_path.read_text())
result = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    cwd=root,
    check=True,
    capture_output=True,
)
paths = sorted(
    p for p in result.stdout.decode().strip("\0").split("\0")
    if p and p not in {"MANIFEST.json", "PACKAGE-VALIDATION.json"}
)
manifest["implementation_status"] = "in_progress"
manifest["files"] = [
    {
        "path": p,
        "bytes": (root / p).stat().st_size,
        "sha256": hashlib.sha256((root / p).read_bytes()).hexdigest(),
    }
    for p in paths
]
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print(f"Updated manifest: {len(paths)} source files")
