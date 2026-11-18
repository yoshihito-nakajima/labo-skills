"""Execution checks for review_coverage.py and the target labels make_packet.py records, on fictional data.

Run with ``python3 -m unittest discover -s .agents/tests -p test_review_coverage.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/reading-book/scripts"
COVERAGE = SCRIPTS / "review_coverage.py"
MAKE_PACKET = SCRIPTS / "make_packet.py"

CHAPTER = r"""\section{Toys}\label{sec:toys}
\begin{definition}\label{def:toy}
A toy is a set with one point.
\end{definition}
\begin{lemma}\label{lem:finite}
Every toy is finite.
\end{lemma}
\termat{lem:finite}{reading}{finite toy}
\begin{proof}
A one-point set is finite.
\end{proof}
\begin{theorem}\label{thm:compact}
Every toy is compact.
\end{theorem}
\begin{proof}
By \cref{lem:finite}.
\end{proof}
\begin{proposition}\label{prop:connected}
Every toy is connected.
\end{proposition}
\begin{proof}
It has no two disjoint nonempty open subsets.
\end{proof}
\begin{corollary}\label{cor:cited}
Toys are nice (cited, no proof here).
\end{corollary}
"""


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True)


class ReviewCoverageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.root = d / "course"
        (self.root / "chapters").mkdir(parents=True)
        (self.root / "chapters/toy.tex").write_text(CHAPTER)
        self.reviews = d / "review"
        self.reviews.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def packet(self, name: str, lines: str, ready=True, claimed=True) -> Path:
        out = self.reviews / name
        r = run(str(MAKE_PACKET), "--root", str(self.root), "--file", "chapters/toy.tex", "--lines", lines,
                "--out", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        if claimed:
            (out / "CLAIMED").write_text("R-1\n")
        if ready:
            (out / "results").mkdir(exist_ok=True)
            (out / "results/READY").write_text("ok\n")
        return out

    def coverage(self, *args: str):
        r = run(str(COVERAGE), *args, "--root", str(self.root), "--files", "chapters/*.tex",
                "--reviews", str(self.reviews), "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def states(self) -> dict:
        rows = self.coverage("list")
        return {r["label"]: r["state"] for r in rows}

    def test_make_packet_records_complete_target_blocks(self):
        out = self.packet("p1", "5-17")
        man = json.loads((out / "manifest.json").read_text())
        self.assertEqual(sorted(man["target_labels"]), ["lem:finite", "thm:compact"])
        self.assertEqual(man["target_partial"], [])
        out2 = self.packet("p2", "12-15")  # theorem without the end of its proof
        man2 = json.loads((out2 / "manifest.json").read_text())
        self.assertEqual(man2["target_labels"], {})
        self.assertEqual(man2["target_partial"], ["thm:compact"])

    def test_states_follow_records_and_canonical_changes(self):
        self.packet("reviewed", "5-17")                         # lem:finite, thm:compact reviewed
        self.packet("claimed", "18-24", ready=False)             # prop:connected in review
        self.packet("unclaimed", "2-4", ready=False, claimed=False)  # def:toy: published only
        st = self.states()
        self.assertEqual(st["lem:finite"], "current")
        self.assertEqual(st["thm:compact"], "current")
        self.assertEqual(st["prop:connected"], "in-review")
        self.assertEqual(st["def:toy"], "unreviewed")
        # re-indexing and re-wrapping are not changes; a changed proof is
        text = CHAPTER.replace(r"\termat{lem:finite}{reading}{finite toy}", r"\index{finite toy}")
        text = text.replace("A one-point set is finite.", "A one-point set\n   is finite.")
        (self.root / "chapters/toy.tex").write_text(text)
        self.assertEqual(self.states()["lem:finite"], "current")
        (self.root / "chapters/toy.tex").write_text(text.replace("By \\cref{lem:finite}.", "By \\cref{lem:finite}; done."))
        self.assertEqual(self.states()["thm:compact"], "changed")

    def test_other_layouts_need_the_proof_and_strip_line_numbers(self):
        case = self.reviews / "legacy"
        (case / "input").mkdir(parents=True)
        lines = CHAPTER.splitlines()
        numbered = "\n".join(f"{i}: {x}" for i, x in enumerate(lines[11:17], 12))  # thm:compact with proof
        (case / "input/target.tex").write_text(numbered + "\n")
        (case / "input/premises.tex").write_text("\n".join(lines[4:7]) + "\n")  # lem:finite statement only
        (case / "READY").write_text("ok\n")
        st = self.states()
        self.assertEqual(st["thm:compact"], "current")
        self.assertEqual(st["lem:finite"], "unreviewed")

    def test_output_cases_and_exclusions_do_not_count(self):
        out = self.packet("toy-output-v1", "5-17")
        man = json.loads((out / "manifest.json").read_text())
        man["kind"] = "output"
        (out / "manifest.json").write_text(json.dumps(man))
        self.packet("parent-written", "18-24")
        excl = Path(self.tmp.name) / "exclude.txt"
        excl.write_text("parent-written  # reviewer was not independent\n")
        rows = self.coverage("list", "--exclude", str(excl))
        st = {r["label"]: r["state"] for r in rows}
        self.assertEqual(st["lem:finite"], "unreviewed")
        self.assertEqual(st["prop:connected"], "unreviewed")

    def test_next_proposes_contiguous_unreviewed_results_with_proofs(self):
        self.packet("reviewed", "5-11")  # lem:finite only
        chunks = self.coverage("next", "--stable-minutes", "0")
        self.assertEqual(len(chunks), 1)
        c = chunks[0]
        self.assertEqual(c["labels"], ["thm:compact", "prop:connected"])
        self.assertEqual((c["start"], c["end"]), (12, 23))
        self.assertTrue(c["stable"])
        groups = Path(self.tmp.name) / "groups.json"
        groups.write_text(json.dumps({"groups": [{"name": "v1", "spans": [
            {"file": "chapters/toy.tex", "start": 1, "end": 17, "priority": True},
            {"file": "chapters/toy.tex", "start": 18, "end": 99, "priority": False}]}]}))
        chunks = self.coverage("next", "--groups", str(groups), "--stable-minutes", "99999")
        self.assertEqual([c["labels"] for c in chunks], [["thm:compact"], ["prop:connected"]])
        self.assertTrue(chunks[0]["priority"])
        self.assertFalse(chunks[0]["stable"])
        groups.write_text(json.dumps({"groups": [
            {"name": "v1", "spans": [{"file": "chapters/toy.tex", "start": 18, "end": 99, "priority": False}]},
            {"name": "v2", "spans": [{"file": "chapters/toy.tex", "start": 1, "end": 17, "priority": True}]}]}))
        chunks = self.coverage("next", "--groups", str(groups), "--stable-minutes", "0", "--group-order")
        self.assertEqual([c["group"] for c in chunks], ["v1", "v2"])  # earlier volume first, even before priority

    def test_next_proposes_changed_results_after_unreviewed_ones(self):
        self.packet("reviewed", "5-17")  # lem:finite, thm:compact
        (self.root / "chapters/toy.tex").write_text(CHAPTER.replace("By \\cref{lem:finite}.", "By \\cref{lem:finite}; done."))
        chunks = self.coverage("next", "--stable-minutes", "0")
        self.assertEqual([(c["state"], c["labels"]) for c in chunks],
                         [("unreviewed", ["prop:connected"]), ("changed", ["thm:compact"])])

    def test_recorded_minor_repair_counts_until_the_next_change(self):
        self.packet("reviewed", "5-17")  # lem:finite, thm:compact
        repaired = CHAPTER.replace("By \\cref{lem:finite}.", "By \\cref{lem:finite}; done.")
        (self.root / "chapters/toy.tex").write_text(repaired)
        self.assertEqual(self.states()["thm:compact"], "changed")
        args = ["--root", str(self.root), "--reviews", str(self.reviews)]
        r = run(str(COVERAGE), "record-repair", "--case", "reviewed", *args)  # severity is required
        self.assertNotEqual(r.returncode, 0)
        r = run(str(COVERAGE), "record-repair", "--case", "reviewed", "--severity", "minor", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("thm:compact", r.stdout)
        rows = {x["label"]: x for x in self.coverage("list")}
        self.assertEqual(rows["thm:compact"]["state"], "current")
        self.assertTrue(rows["thm:compact"]["accepted_repair"])
        self.assertFalse(rows["lem:finite"]["accepted_repair"])  # unchanged: the review itself is current
        (self.root / "chapters/toy.tex").write_text(repaired.replace("; done.", "; done again."))
        self.assertEqual(self.states()["thm:compact"], "changed")
        self.packet("unreturned", "18-24", ready=False)
        r = run(str(COVERAGE), "record-repair", "--case", "unreturned", "--severity", "minor", *args)
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
