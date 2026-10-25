"""Exercise cadence, substantive question and append-only peer receipt gates."""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import validate_agent_flow as policy


class MeetingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        directory = self.root / "work/agent-journals"
        directory.mkdir(parents=True)
        self.own = directory / "owner.md"
        self.peer = directory / "peer.md"
        self.peer.write_text("# Peer\nPersona: testing\n## Iteration 1\nActual work.\n", encoding="utf-8", newline="\n")

    def meeting(self, count=5):
        data = self.peer.read_bytes()
        receipt = f"- Read: work/agent-journals/peer.md | bytes: {len(data)} | sha256: {hashlib.sha256(data).hexdigest()}\n"
        rows = [f"| Q{i} | WORK-0013 | How does logged change number {i} affect the contract? | peer | open |" for i in range(1, count + 1)]
        return "## Meeting after iteration 3\n" + receipt + "\n".join(rows) + "\n"

    def write(self, extra=""):
        self.own.write_text("# Owner\nPersona: orchestrator\n## Iteration 1\nA\n## Iteration 2\nB\n## Iteration 3\nC\n" + extra, encoding="utf-8")

    def test_due_meeting_and_fourth_iteration_are_rejected(self):
        self.write()
        self.assertTrue(any("due" in e for e in policy.journal_errors(self.own, self.root)))
        self.write("## Iteration 4\nD\n")
        self.assertTrue(any("more than 3" in e for e in policy.journal_errors(self.own, self.root)))

    def test_five_questions_and_real_peer_prefix_allow_continuation(self):
        self.write(self.meeting() + "## Iteration 4\nIndependent work\n")
        self.assertEqual([], policy.journal_errors(self.own, self.root))
        with self.peer.open("a", encoding="utf-8") as stream:
            stream.write("New answer appended.\n")
        self.assertEqual([], policy.journal_errors(self.own, self.root))

    def test_two_column_response_bookkeeping_does_not_add_meeting_questions(self):
        response = "\n## Responses to peer questions\n| ID | Answer |\n| --- | --- |\n| Q6 | Answered in peer journal. |\n"
        self.write(self.meeting() + response)
        self.assertEqual([], policy.journal_errors(self.own, self.root))
        self.write(self.meeting(count=4) + response)
        self.assertTrue(any("5 distinct" in e for e in policy.journal_errors(self.own, self.root)))

    def test_missing_questions_and_rewritten_peer_are_rejected(self):
        self.write(self.meeting(count=4))
        self.assertTrue(any("5 distinct" in e for e in policy.journal_errors(self.own, self.root)))
        self.write(self.meeting())
        self.peer.write_text("rewritten", encoding="utf-8")
        self.assertTrue(any("rewritten" in e for e in policy.journal_errors(self.own, self.root)))

    def test_counter_reset_and_empty_respondent_fail(self):
        self.write(self.meeting().replace("| peer |", "| |") + "## Iteration 1\nReset\n")
        issues = policy.journal_errors(self.own, self.root)
        self.assertTrue(any("consecutive" in e for e in issues))
        self.assertTrue(any("respondent" in e for e in issues))

    def test_receipt_survives_only_line_ending_conversion(self):
        self.write(self.meeting())
        original = self.peer.read_bytes()
        self.peer.write_bytes(original.replace(b"\n", b"\r\n"))
        self.assertEqual([], policy.journal_errors(self.own, self.root))

    def test_self_duplicate_and_missing_peer_receipts_fail(self):
        meeting = self.meeting()
        receipt = next(line for line in meeting.splitlines() if line.startswith("- Read:"))
        self.write(meeting + receipt + "\n")
        self.assertTrue(any("distinct peer" in e for e in policy.journal_errors(self.own, self.root)))
        self.write(meeting.replace("peer.md", "owner.md"))
        self.assertTrue(any("distinct peer" in e for e in policy.journal_errors(self.own, self.root)))
        self.write(meeting.replace("peer.md", "missing.md"))
        self.assertTrue(any("resolve" in e for e in policy.journal_errors(self.own, self.root)))

    def test_persona_is_required_in_each_agent_journal(self):
        self.own.write_text("# Owner\n## Iteration 1\nA\n", encoding="utf-8")
        self.assertTrue(any("persona" in e for e in policy.journal_errors(self.own, self.root)))


if __name__ == "__main__":
    unittest.main()
