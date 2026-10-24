"""Boundary checks for verified Android staging; sanitized tiny fixture only."""
import hashlib
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch
from tools import prepare_android_inference as staging


class VerifiedStagingTests(unittest.TestCase):
    def directory_link(self, link, target):
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                raise
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                           capture_output=True, check=True, timeout=10)
        self.addCleanup(lambda: os.rmdir(link))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "workspace"
        self.root.mkdir()
        self.patcher = patch.object(staging, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.source = self.root / "source"
        self.source.write_bytes(b"sanitized fixture")
        self.expected = (self.source.stat().st_size, hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_copy_verified_then_replaces_existing(self):
        destination = self.root / "assets/model"
        staging.verified_copy(self.source, destination, self.expected)
        self.assertEqual(destination.read_bytes(), b"sanitized fixture")
        self.assertFalse(destination.with_suffix(".partial").exists())

    def test_mismatch_does_not_replace_destination(self):
        destination = self.root / "model"
        destination.write_bytes(b"keep")
        with self.assertRaises(staging.CheckError):
            staging.verified_copy(self.source, destination, (1, "0" * 64))
        self.assertEqual(destination.read_bytes(), b"keep")

    def test_rejects_explicit_external_destination_and_source(self):
        outside = self.base / "outside"
        outside.write_bytes(b"keep")
        with self.assertRaises(staging.CheckError):
            staging.verified_copy(self.source, outside, self.expected)
        with self.assertRaises(staging.CheckError):
            staging.verified_copy(outside, self.root / "model", self.expected)
        self.assertEqual(outside.read_bytes(), b"keep")

    def test_partial_symlink_cannot_redirect_write(self):
        outside = self.base / "outside"
        outside.mkdir()
        partial = self.root / "model.partial"
        self.directory_link(partial, outside)
        with self.assertRaises(staging.CheckError):
            staging.verified_copy(self.source, self.root / "model", self.expected)
        self.assertEqual(list(outside.iterdir()), [])

    def test_nested_cmake_output_checks_before_execute(self):
        install = self.root / ".artifacts/native/android-1.5.1"
        install.mkdir(parents=True)
        outside = self.base / "outside-dir"
        outside.mkdir()
        self.directory_link(install / "examples", outside)
        with patch.object(staging, "execute") as execute:
            self.assertEqual(staging.run(".artifacts/checks/negative", 1), 1)
            execute.assert_not_called()
        self.assertEqual(list(outside.iterdir()), [])

    def test_notice_inventory_repeated_staging_is_identical(self):
        source, install, ndk = (self.root / name for name in ("source-tree", "install", "ndk"))
        component_paths = [source, source / "extension/llm/tokenizers", ndk, install / "kleidiai-source"]
        component_paths += [source / "backends/xnnpack/third-party" / name for name in
                            ("XNNPACK", "pthreadpool", "cpuinfo", "FP16", "FXdiv")]
        component_paths += [source / "third-party" / name for name in ("flatbuffers", "gflags", "json")]
        component_paths += [source / "kernels/optimized/third-party/eigen"]
        component_paths += [source / "extension/llm/tokenizers/third-party" / name for name in
                            ("abseil-cpp", "json", "pcre2", "re2", "sentencepiece")]
        for component in component_paths:
            component.mkdir(parents=True, exist_ok=True)
            (component / "LICENSE").write_bytes(b"sanitized notice")
        assets = self.root / "assets"
        with patch.object(staging, "git", return_value=staging.RUNTIME_REVISION):
            first = staging.stage_notices(source, install, ndk, assets)
            original = (self.root / first["path"]).read_bytes()
            second = staging.stage_notices(source, install, ndk, assets)
        self.assertEqual(first, second)
        self.assertEqual(first["components"], 18)
        self.assertEqual(original, (self.root / second["path"]).read_bytes())
        self.assertFalse((assets / "runtime-notices/inventory.json.partial").exists())


if __name__ == "__main__":
    unittest.main()
