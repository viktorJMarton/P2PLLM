#!/usr/bin/env python3
"""Refresh the source inventory after intentional repository changes.

The original handoff remains recoverable from the first Git commit.
"""
import hashlib
import json
from pathlib import Path
from source_inventory import HASH_MODE, INVENTORY_EXCLUSIONS, inventory_bytes, source_paths

root = Path(__file__).resolve().parents[1]
manifest_path = root / "MANIFEST.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
paths = [p for p in source_paths(root) if p.name not in INVENTORY_EXCLUSIONS]
manifest["implementation_status"] = "in_progress"
manifest["hash_mode"] = HASH_MODE
manifest["files"] = [
    {
        "path": p.relative_to(root).as_posix(),
        "bytes": len(inventory_bytes(p)),
        "sha256": hashlib.sha256(inventory_bytes(p)).hexdigest(),
    }
    for p in paths
]
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"Updated manifest: {len(paths)} source files")
