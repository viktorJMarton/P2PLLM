"""Verify the native FlatBuffers compiler shipped by the locked Windows wheel."""

import hashlib
from pathlib import Path
import zipfile


class RuntimeArtifactError(ValueError):
    """Fixed artifact verification failure, without filesystem diagnostics."""


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def recheck_flatc(record, venv):
    """A worker rechecks the exact dedicated-venv executable before using it."""
    try:
        expected = Path(venv) / "Lib/site-packages/executorch/data/bin/flatc.exe"
        executable = Path(record["executable"])
        if (not executable.is_absolute() or executable.is_symlink()
                or executable.resolve() != expected.resolve()
                or not executable.resolve().is_relative_to(Path(venv).resolve())
                or not executable.is_file() or _sha256(executable) != record["sha256"]):
            raise RuntimeArtifactError("flatc_installed_binary_mismatch")
        return str(executable.resolve())
    except (OSError, KeyError, TypeError) as error:
        raise RuntimeArtifactError("flatc_installed_binary_unavailable") from error


def verified_flatc(root, baseline, python):
    """Return native-tool provenance only after exact wheel/member verification.

    No extraction, installation, PATH lookup or execution. This Windows-wheel
    route makes no assertion about other host distributions.
    """
    try:
        venv = Path(root).resolve() / ".artifacts/venvs/qwen-export"
        if Path(python).resolve() != (venv / "Scripts/python.exe").resolve():
            raise RuntimeArtifactError("flatc_unexpected_export_venv")
        package = next(p for p in baseline["runtime"]["dependency_resolution"]["packages"]
                       if p["name"] == "executorch")
        wheels = [path for path in (venv / "wheelhouse").glob("executorch-*.whl")
                  if not path.is_symlink() and _sha256(path) == package["sha256"]]
        if len(wheels) != 1:
            raise RuntimeArtifactError("flatc_official_wheel_unavailable")
        member = "executorch/data/bin/flatc.exe"
        with zipfile.ZipFile(wheels[0]) as archive:
            info = archive.getinfo(member)
            if not 2 <= info.file_size <= 64 * 1024 * 1024:
                raise RuntimeArtifactError("flatc_wheel_member_invalid")
            raw = archive.read(member)
        if not raw.startswith(b"MZ"):
            raise RuntimeArtifactError("flatc_wheel_member_invalid")
        record = {"executable": str((venv / "Lib/site-packages" / member).resolve()),
                  "sha256": hashlib.sha256(raw).hexdigest(),
                  "wheel_sha256": package["sha256"], "wheel_member": member}
        recheck_flatc(record, venv)
        return record
    except (OSError, KeyError, StopIteration, TypeError, zipfile.BadZipFile) as error:
        raise RuntimeArtifactError("flatc_wheel_verification_failed") from error
