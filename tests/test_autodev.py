#!/usr/bin/env python3
"""Contract tests for the deterministic development planner; no Codex launch."""
import json
from pathlib import Path
import tempfile
import unittest
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import autodev


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "work").mkdir()
        (self.root / "config").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def put(self, wid, status, deps="none", score=3):
        folder = self.root / "work" / f"{wid}-example"
        folder.mkdir()
        (folder / "brief.md").write_text(
            f"# {wid}\nStatus: {status}\nDependencies: {deps}\n\n## Objective\nTest\n")
        path = self.root / "config" / "autodev.tasks.json"
        doc = json.loads(path.read_text()) if path.exists() else {"version": 1, "tasks": {}}
        doc["tasks"][wid] = dict(impact=score, unblocks=3, confidence=3,
                                  effort=2, risk=2, instruction="Perform a scoped test.")
        path.write_text(json.dumps(doc))

    def test_selects_in_progress_and_blocks_dependencies(self):
        self.put("WORK-0001", "in_progress")
        self.put("WORK-0002", "not_started", "WORK-0001", score=5)
        result = autodev.plan(self.root)
        self.assertEqual(result["selected"]["id"], "WORK-0001")
        self.assertEqual(result["blocked"][0]["reason"], "dependencies")

    def test_verified_dependency_unblocks(self):
        self.put("WORK-0001", "verified")
        self.put("WORK-0002", "not_started", "WORK-0001")
        self.assertEqual(autodev.plan(self.root)["selected"]["id"], "WORK-0002")

    def test_cycle_rejected(self):
        self.put("WORK-0001", "not_started", "WORK-0002")
        self.put("WORK-0002", "not_started", "WORK-0001")
        with self.assertRaisesRegex(ValueError, "cycle"):
            autodev.plan(self.root)

    def test_unknown_dependency_rejected(self):
        self.put("WORK-0001", "not_started", "WORK-0099")
        with self.assertRaisesRegex(ValueError, "Invalid dependency"):
            autodev.plan(self.root)

    def test_missing_policy_rejected(self):
        self.put("WORK-0001", "not_started")
        path = self.root / "config" / "autodev.tasks.json"
        path.write_text('{"version":1,"tasks":{}}')
        with self.assertRaisesRegex(ValueError, "differ"):
            autodev.plan(self.root)

    def test_blocked_never_selected(self):
        self.put("WORK-0001", "blocked")
        result = autodev.plan(self.root)
        self.assertIsNone(result["selected"])
        self.assertEqual(result["status"], "no_eligible_work")


    @unittest.skipUnless(autodev.os.name == "posix", "POSIX-only lease")
    def test_single_execution_lease(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        with autodev.execution_lease(self.root):
            with self.assertRaisesRegex(RuntimeError, "already owns"):
                with autodev.execution_lease(self.root):
                    pass
        with autodev.execution_lease(self.root):
            pass

    def test_append_event_is_valid_jsonl(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        autodev.append_event(self.root, {"run_id": "a", "state": "started"})
        autodev.append_event(self.root, {"run_id": "a", "state": "ended", "exit_code": 0})
        lines = autodev.git_metadata_path(self.root, "autodev-runs.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[1])["exit_code"], 0)


    def test_status_detects_unreconciled_run(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        autodev.append_event(self.root, {"run_id": "x", "state": "started"})
        self.assertEqual(len(autodev.run_status(self.root)["active_or_unreconciled"]), 1)
        autodev.append_event(self.root, {"run_id": "x", "state": "ended", "exit_code": 124})
        self.assertEqual(autodev.run_status(self.root)["active_or_unreconciled"], [])

    def test_status_rejects_corrupt_journal(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        autodev.git_metadata_path(self.root, "autodev-runs.jsonl").write_text("not-json\\n")
        with self.assertRaisesRegex(ValueError, "Corrupt"):
            autodev.run_status(self.root)


if __name__ == "__main__":
    unittest.main()
