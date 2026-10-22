"""Protect bootstrap boundaries without network access or actual tool installs."""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io
import json
import subprocess
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import dev_env


class BootstrapTests(unittest.TestCase):
    def test_cached_archive_must_match_pinned_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / "downloads").mkdir()
            archive = cache / "downloads/package.zip"
            archive.write_bytes(b"original")
            package = {"url": "https://example.invalid/package.zip",
                       "sha256": hashlib.sha256(b"original").hexdigest(), "size": 8}
            self.assertEqual(archive, dev_env.download(package, cache))
            archive.write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                dev_env.download(package, cache)

    def test_zip_cannot_escape_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as source:
                source.writestr("../../outside.txt", "unsafe")
            with self.assertRaises(ValueError):
                dev_env.install_zip(archive, root / "installed/tool", root / "staging")
            self.assertFalse((root / "outside.txt").exists())

    def test_package_install_is_idempotent_without_overwriting_local_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "tool.zip"
            with zipfile.ZipFile(archive, "w") as source:
                source.writestr("tool/source.properties", "Pkg.Revision=1")
            destination = root / "installed/tool"
            dev_env.install_zip(archive, destination, root / "staging")
            self.assertEqual("Pkg.Revision=1", (destination / "source.properties").read_text())
            dev_env.install_zip(archive, destination, root / "staging")
            self.assertEqual("Pkg.Revision=1", (destination / "source.properties").read_text())

    def test_fresh_jdk_zip_layout_is_activatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "jdk.zip"
            with zipfile.ZipFile(archive, "w") as source:
                source.writestr("jdk-wrapper/bin/java.exe", "fixture-not-executable")
            destination = root / "jdk-17.0.20.1"
            dev_env.install_zip(archive, destination, root / "staging")
            env = dev_env.environment(root, {"jdk": {"version": "17.0.20.1"}})
            self.assertEqual(str(destination), env["JAVA_HOME"])

    def test_doctor_rejects_wrong_version_even_when_commands_succeed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            java = root / "jdk-17.0.20.1/bin/java.exe"
            java.parent.mkdir(parents=True)
            java.write_text("fixture")
            config = {"jdk": {"version": "17.0.20.1"}, "tools": {"rust": "1.88.0", "cargo_ndk": "3.5.4"}}
            reply = subprocess.CompletedProcess([], 0, stdout="wrong-version", stderr="")
            with patch.object(dev_env.subprocess, "run", return_value=reply), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(2, dev_env.doctor(root, config))
            self.assertIn('"version_matches": false', output.getvalue())

    def test_doctor_rejects_near_versions_with_all_sdk_files_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            required = ["jdk-17.0.20.1/bin/java.exe", "android-sdk/platforms/android-35/android.jar",
                "android-sdk/build-tools/35.0.0/aapt2.exe", "android-sdk/cmdline-tools/16.0/bin/sdkmanager.bat",
                "android-sdk/ndk/27.0.12077973/toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe"]
            for name in required:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture")
            config = {"jdk": {"version": "17.0.20.1"}, "tools": {"rust": "1.88.0", "cargo_ndk": "3.5.4"}}
            for observed in ("13.5.4", "3.5.40", "3.5.4-beta", "3.5.4"):
                replies = [subprocess.CompletedProcess([], 0, stdout=value, stderr="") for value in
                    ("openjdk version 17.0.20.1", "javac 17.0.20.1", "rustc 1.88.0", "cargo-ndk " + observed)]
                with patch.object(dev_env.subprocess, "run", side_effect=replies), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(0 if observed == "3.5.4" else 2, dev_env.doctor(root, config))
                report = json.loads(output.getvalue())
                self.assertEqual([], report["missing_sdk_files"])
                self.assertEqual(observed == "3.5.4", report["tools"][-1]["version_matches"])


if __name__ == "__main__":
    unittest.main()
