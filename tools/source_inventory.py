"""Shared source inventory, independent of checkout line endings and path syntax.

utf8-lf-v1 normalizes CRLF in UTF-8 text without NULs. Other files retain their
exact bytes. This is a source inventory convention, never an artifact checksum.
"""

from pathlib import Path
import subprocess

HASH_MODE = "utf8-lf-v1"
INVENTORY_EXCLUSIONS = {"MANIFEST.json", "PACKAGE-VALIDATION.json"}


def source_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root.resolve().as_posix()}",
         "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, capture_output=True, check=True,
    )
    return [root / name for name in sorted(set(
        result.stdout.decode("utf-8").strip("\0").split("\0")
    )) if name]


def inventory_bytes(path: Path, mode: str = HASH_MODE) -> bytes:
    data = path.read_bytes()
    if mode == "raw":
        return data
    if mode != HASH_MODE:
        raise ValueError(f"Unsupported inventory hash mode: {mode}")
    if b"\0" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n")
