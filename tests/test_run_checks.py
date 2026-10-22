"""Behavioral checks with isolated Git repositories and harmless fake commands."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile


SPEC = importlib.util.spec_from_file_location("run_checks", Path(__file__).resolve().parents[1] / "tools/run_checks.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.config = self.root / "config/check-profiles.json"
        self.config.parent.mkdir()
        self.profile = {"description": "Sanitized fixture", "commands": [self.command("ok", "pass")], "artifacts": []}
        self.save_profile()
        (self.root / ".gitignore").write_text(".artifacts/\n", encoding="utf-8")
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "fixture")

    def git(self, *args):
        return subprocess.run(["git", "-c", f"safe.directory={self.root}", *args], cwd=self.root,
                              check=True, capture_output=True, text=True).stdout.strip()

    @staticmethod
    def command(identifier, script, timeout=10):
        return {"id": identifier, "argv": ["{python}", "-c", script], "timeout_seconds": timeout}

    def save_profile(self):
        self.config.write_text(json.dumps({"schema_version": 1, "profiles": {"fixture": self.profile}}), encoding="utf-8")

    def run_profile(self, **kwargs):
        self.save_profile()
        return runner.run_profile(self.root, "fixture", "WORK-0009", "test-run", **kwargs)

    def report(self):
        return json.loads((self.root / ".artifacts/checks/WORK-0009/test-run/fixture/report.json").read_text(encoding="utf-8"))

    def test_success_captures_exact_command_and_revision_without_output(self):
        self.profile["commands"] = [self.command("ok", "print('synthetic-output')")]
        self.save_profile()
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "profile")
        self.assertEqual(self.run_profile(), 0)
        report = self.report()
        self.assertEqual(report["git"], {"head": self.git("rev-parse", "HEAD"), "dirty": False})
        self.assertEqual(report["commands"][0]["argv"][0], sys.executable)
        self.assertEqual(report["commands"][0]["exit_code"], 0)
        self.assertNotIn("stdout", report["commands"][0])
        self.assertIn("+00:00", report["started_at"])

    def test_failed_command_and_missing_executable_preserve_failure(self):
        self.profile["commands"] = [self.command("fail", "raise SystemExit(7)"),
                                    {"id": "missing", "argv": ["no-such-p2pllm-fixture-command-123"], "timeout_seconds": 5}]
        self.assertEqual(self.run_profile(bundle=True), 1)
        report = self.report()
        self.assertEqual(report["status"], "failed")
        self.assertEqual([c["status"] for c in report["commands"]], ["failed", "not_run"])
        self.assertEqual(report["commands"][0]["exit_code"], 7)
        self.assertFalse(list(self.root.rglob("bundle.zip")))

    def test_missing_executable_is_unavailable(self):
        self.profile["commands"] = [{"id": "missing", "argv": ["no-such-p2pllm-fixture-command-123"], "timeout_seconds": 5}]
        self.assertEqual(self.run_profile(), 2)
        self.assertEqual(self.report()["commands"][0]["reason"], "executable_not_found")

    def test_timeout_is_failure(self):
        self.profile["commands"] = [self.command("slow", "import time; time.sleep(30)", timeout=1)]
        self.assertEqual(self.run_profile(), 1)
        self.assertEqual(self.report()["commands"][0]["reason"], "timeout")

    def test_timeout_stops_descendants_before_artifact_mutation(self):
        child = "import time; from pathlib import Path; time.sleep(3); Path('orphan-marker').touch()"
        parent = f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(30)"
        self.profile["commands"] = [self.command("parent", parent, timeout=1)]
        self.assertEqual(self.run_profile(), 1)
        time.sleep(3)
        self.assertFalse((self.root / "orphan-marker").exists())
        self.assertEqual(self.report()["commands"][0]["reason"], "timeout")

    def test_source_changes_fail_and_record_both_fingerprints(self):
        self.profile["commands"] = [self.command("mutation", "from pathlib import Path; Path('source.txt').write_text('fixture')")]
        self.assertEqual(self.run_profile(bundle=True), 1)
        report = self.report()
        self.assertNotEqual(report["source_before"]["sha256"], report["source_after"]["sha256"])
        self.assertEqual(report["reason"], "Source changed during checks")
        self.assertFalse(list(self.root.rglob("bundle.zip")))

    def test_empty_and_declared_unavailable_profiles_do_not_pass(self):
        for index, profile in enumerate([
            {"commands": [], "artifacts": []},
            {"commands": [self.command("must-not-run", "raise SystemExit(99)")], "artifacts": [],
             "unavailable_reason": "Device required"},
        ]):
            self.profile = profile
            self.assertEqual(self.run_profile(output_dir=f".artifacts/case-{index}", bundle=True), 2)
            report = json.loads((self.root / f".artifacts/case-{index}/report.json").read_text())
            self.assertEqual(report["commands"], [])
            self.assertFalse((self.root / f".artifacts/case-{index}/bundle.zip").exists())

    def test_dirty_source_is_recorded(self):
        (self.root / "modified.txt").write_text("sanitized fixture", encoding="utf-8")
        self.assertEqual(self.run_profile(), 0)
        self.assertTrue(self.report()["git"]["dirty"])

    def test_missing_git_provenance_cannot_pass(self):
        # Point Git to an invalid repository, without mocking command behavior.
        old_git = self.root / ".git"
        old_git.rename(self.root / "fixture-git-moved")
        self.assertEqual(self.run_profile(), 2)
        self.assertIsNone(self.report()["git"]["head"])

    def test_missing_or_directory_artifact_fails_without_bundle(self):
        for index, artifact in enumerate(["build/absent.bin", "config"]):
            self.profile["artifacts"] = [artifact]
            self.assertEqual(self.run_profile(output_dir=f".artifacts/missing-{index}"), 1)

    def test_artifact_hashes_match_archived_bytes(self):
        artifact = self.root / "build/program.bin"
        artifact.parent.mkdir()
        contents = b"sanitized binary fixture\x00\xff"
        artifact.write_bytes(contents)
        (self.root / "sensitive-unlisted.txt").write_text("not for collection", encoding="utf-8")
        self.profile["artifacts"] = ["build/program.bin"]
        self.assertEqual(self.run_profile(bundle=True), 0)
        with zipfile.ZipFile(next(self.root.rglob("bundle.zip"))) as archive:
            self.assertEqual(set(archive.namelist()), {"report.json", "artifacts/build/program.bin", "manifest.json"})
            manifest = json.loads(archive.read("manifest.json"))
            for entry in manifest["files"]:
                payload = archive.read(entry["path"])
                self.assertEqual(entry["sha256"], hashlib.sha256(payload).hexdigest())
                self.assertEqual(entry["size_bytes"], len(payload))
            self.assertEqual(archive.read("artifacts/build/program.bin"), contents)

    def test_unsafe_report_destinations_are_rejected_before_commands(self):
        marker = self.root / "executed"
        self.profile["commands"] = [self.command("marker", "from pathlib import Path; Path('executed').touch()")]
        for destination in ["../escape", str(self.root.parent / "outside-evidence"), ".artifacts/../escape"]:
            with self.subTest(destination=destination), self.assertRaises(runner.CheckError):
                self.run_profile(output_dir=destination)
        self.assertFalse(marker.exists())

    def test_unsafe_artifacts_are_rejected(self):
        for artifact in ["../outside", str(self.root / "absolute.bin"), ".artifacts/checks/WORK-0009/test-run/fixture/report.json"]:
            self.profile["artifacts"] = [artifact]
            with self.subTest(artifact=artifact), self.assertRaises(runner.CheckError):
                self.run_profile(bundle=True)

    def test_symlink_artifact_and_destination_are_rejected(self):
        target = self.root / "real"
        target.mkdir()
        (target / "fixture.bin").write_bytes(b"fixture")
        link = self.root / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Host does not permit symlink creation: {error.winerror if hasattr(error, 'winerror') else error.errno}")
        self.profile["artifacts"] = ["link/fixture.bin"]
        with self.assertRaises(runner.CheckError):
            self.run_profile()
        self.profile["artifacts"] = []
        with self.assertRaises(runner.CheckError):
            self.run_profile(output_dir="link/evidence")

    def test_existing_output_does_not_overwrite_or_run_commands(self):
        self.assertEqual(self.run_profile(bundle=True), 0)
        report = next(self.root.rglob("report.json"))
        before = report.read_bytes()
        self.profile["commands"] = [self.command("marker", "from pathlib import Path; Path('executed').touch()")]
        with self.assertRaises(runner.CheckError):
            self.run_profile(bundle=True)
        self.assertEqual(report.read_bytes(), before)
        self.assertFalse((self.root / "executed").exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junction_is_rejected_without_symlink_privilege(self):
        target = self.root / "real"
        target.mkdir()
        link = self.root / "junction"
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                       check=True, capture_output=True)
        self.assertTrue(link.is_junction())
        with self.assertRaises(runner.CheckError):
            self.run_profile(output_dir="junction/evidence")
        self.profile["artifacts"] = ["junction/fixture.bin"]
        with self.assertRaises(runner.CheckError):
            self.run_profile()

    def test_bundle_collision_preserves_existing_file_and_fails(self):
        destination = ".artifacts/checks/WORK-0009/test-run/fixture/bundle.zip"
        script = f"from pathlib import Path; Path({destination!r}).write_bytes(b'collision fixture')"
        self.profile["commands"] = [self.command("collision", script)]
        self.assertEqual(self.run_profile(bundle=True), 1)
        self.assertEqual((self.root / destination).read_bytes(), b"collision fixture")
        self.assertEqual(self.report()["reason"], "Bundle creation failed")

    def test_invalid_profile_and_identifiers_fail(self):
        self.profile["commands"][0]["timeout_seconds"] = True
        with self.assertRaises(runner.CheckError):
            self.run_profile()
        self.profile["commands"] = []
        self.save_profile()
        with self.assertRaises(runner.CheckError):
            runner.run_profile(self.root, "fixture", "WORK-0009", "../unsafe")


if __name__ == "__main__":
    unittest.main()
