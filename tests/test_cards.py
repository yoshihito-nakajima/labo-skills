"""Execute check_cards.py on small fictional card data."""

from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest

CHECK = Path(__file__).resolve().parents[1] / "skills/reading-reference/scripts/check_cards.py"


def pair(text, source):
    return {"text": text, "source": source}


GOOD = {
    "roots": [{"id": "R1", "question": "measure along the set", "source": "Survey 2020, p.4",
               "shared_example": pair("rolled sheet", "Survey 2020, Fig.5"), "nodes": ["graph-method"]}],
    "nodes": {"graph-method": {
        "uses": ["the sheet from the previous unit"], "roots": ["R1"],
        "shared": pair("rolled sheet", "Survey 2020, Fig.5"),
        "lens": pair("shortest paths approximate geodesics", "Survey 2020, p.10"),
        "applied": pair("the sheet unrolled", "Survey 2020, Fig.5(a)"),
        "specific": pair("handwritten twos", "Author 1999, Fig.1B"),
        "limit": pair("dense matrices", "speaker's reading"),
        "code": "graph method"}},
}


class CheckCardsTests(unittest.TestCase):
    def run_check(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cards.json"
            path.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(CHECK), str(path), "--json"],
                                    capture_output=True, text=True)
            return result.returncode, [p["problem"] for p in json.loads(result.stdout)]

    def test_well_formed_cards_pass(self):
        good = copy.deepcopy(GOOD)
        good["nodes"]["graph-method"]["limit"]["searched"] = [
            {"where": "Survey 2020, §5", "outcome": "not found in the searched scope"}]
        self.assertEqual(self.run_check(good), (0, []))

    def test_missing_source_note_place_and_unknown_root_are_reported(self):
        bad = copy.deepcopy(GOOD)
        node = bad["nodes"]["graph-method"]
        node["lens"] = pair("shortest paths", "")
        node["specific"] = pair("handwritten twos", "詳細版の応用例")
        node["roots"] = ["R1", "R9"]
        del node["limit"]
        code, problems = self.run_check(bad)
        self.assertEqual(code, 1)
        text = " | ".join(problems)
        for expected in ("lens has no source", "points into the note itself", "unknown root R9", "missing limit"):
            self.assertIn(expected, text)

    def test_writers_reading_needs_a_recorded_search(self):
        bad = copy.deepcopy(GOOD)
        self.assertIn("limit is the writer's reading without a recorded search (add 'searched')",
                      self.run_check(bad)[1])
        ok = copy.deepcopy(GOOD)
        ok["nodes"]["graph-method"]["limit"]["searched"] = [
            {"where": "Survey 2020, §5", "outcome": "found, does not state it"}]
        self.assertEqual(self.run_check(ok), (0, []))

    def test_todo_lists_open_questions(self):
        data = copy.deepcopy(GOOD)
        data["nodes"]["graph-method"]["limit"]["searched"] = [
            {"where": "Survey 2020, §5", "outcome": "not found in the searched scope"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cards.json"
            path.write_text(json.dumps(data))
            out = subprocess.run([sys.executable, str(CHECK), str(path), "--todo", "--target", "Survey 2020", "--json"],
                                 capture_output=True, text=True)
        items = {(i["field"], i["why"]) for i in json.loads(out.stdout)}
        self.assertIn(("limit", "writer's reading"), items)
        self.assertIn(("lens", "rests only on the target paper"), items)
        self.assertNotIn(("specific", "rests only on the target paper"), items)

    def test_plain_string_fields_and_not_applicable_marker(self):
        bad = copy.deepcopy(GOOD)
        bad["nodes"]["graph-method"]["applied"] = "unrolled (Survey 2020, Fig.5)"
        self.assertIn("applied is not a {text, source} pair", self.run_check(bad)[1])
        ok = copy.deepcopy(GOOD)
        ok["nodes"]["graph-method"]["applied"] = pair("—", "n/a: no shared figure in the survey")
        ok["nodes"]["graph-method"]["limit"]["searched"] = [
            {"where": "Survey 2020, §5", "outcome": "not found in the searched scope"}]
        self.assertEqual(self.run_check(ok)[0], 0)


if __name__ == "__main__":
    unittest.main()
