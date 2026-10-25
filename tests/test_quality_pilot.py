"""Public-case grading boundaries; no model or network execution."""
import json
from pathlib import Path
import tempfile
import unittest
from tools import quality_pilot as pilot
from tools import quality_reference as reference


class PublicPilotTests(unittest.TestCase):
    def test_frozen_public_corpus_and_rendered_g01(self):
        cases = pilot.load_cases(reference.ROOT)
        self.assertEqual(tuple(c["id"] for c in cases), pilot.CASE_IDS)
        self.assertEqual(pilot.render_case(cases[0]), reference.rendered_greeting(reference.ROOT))

    def test_changed_or_private_fixture_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / reference.CORPUS
            path.parent.mkdir(parents=True)
            path.write_text('{"schema_version":1,"cases":[{"id":"G01","prompt":"private"}]}')
            with self.assertRaises(reference.CheckError):
                pilot.load_cases(root)

    def test_exact_answers_do_not_accept_expected_keyword_in_nonsense(self):
        case = {"expected_kind": "exact", "expected": "42"}
        self.assertTrue(pilot.deterministic_check(case, " 42\n"))
        self.assertFalse(pilot.deterministic_check(case, "42 repeated wrong answer 42"))
        self.assertIsNone(pilot.deterministic_check({"expected_kind": "review"}, "synthetic"))

    def test_json_numeric_equivalence_and_no_duplicate_or_extra_content(self):
        case = {"expected_kind": "json", "expected": {"nev": "Éva", "kor": 31}}
        for value in ("31", "31.0", "3.1e1"):
            self.assertTrue(pilot.deterministic_check(case, '{"nev":"Éva","kor":'+value+'}'))
        for value in ('{"nev":"Éva","kor":"31"}', '{"nev":"Éva","kor":31,"kor":31}',
                      '{"nev":"Éva","kor":31,"extra":0}', '{"nev":"Éva","kor":NaN}',
                      '{"nev":"Éva","kor":31.000000000000000001}',
                      '```json\n{"nev":"Éva","kor":31}\n```'):
            self.assertFalse(pilot.deterministic_check(case, value))


if __name__ == "__main__":
    unittest.main()
