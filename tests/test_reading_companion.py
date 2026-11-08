"""Build and check the fictional reading-companion example, and exercise the main refusals."""

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills/reading-companion"
BUILD = SKILL / "scripts/build_companion.py"
CHECK = SKILL / "scripts/check_companion.py"
EXAMPLE = SKILL / "assets/example"


class ReadingCompanionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "example"
        shutil.copytree(EXAMPLE, self.dir)
        self.spec = self.dir / "companion.json"
        self.out = Path(self.tmp.name) / "out/index.html"

    def tearDown(self):
        self.tmp.cleanup()

    def run_py(self, script, *args):
        return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)

    def edit(self, fn):
        d = json.loads(self.spec.read_text())
        fn(d)
        self.spec.write_text(json.dumps(d))

    def test_example_builds_and_passes(self):
        r = self.run_py(BUILD, str(self.spec), "--out", str(self.out))
        self.assertEqual(r.returncode, 0, r.stdout)
        page = self.out.read_text()
        self.assertIn("def neighbour_graph", page)          # authors' code embedded verbatim
        self.assertNotIn("/*__COMPANION_DATA__*/", page)
        c = self.run_py(CHECK, str(self.spec), str(self.out))
        self.assertEqual(c.returncode, 0, c.stdout)

    def test_background_is_required(self):
        self.edit(lambda d: d["features"][0].update(background=""))
        r = self.run_py(BUILD, str(self.spec), "--out", str(self.out))
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing background", r.stdout)

    def test_parameter_token_must_be_on_its_line(self):
        self.edit(lambda d: d["features"][0]["author_code"]["params"][0].update(token="k=99"))
        r = self.run_py(BUILD, str(self.spec), "--out", str(self.out))
        self.assertIn("not on line", r.stdout)

    def test_every_grid_point_needs_a_result(self):
        self.edit(lambda d: d["features"][0]["author_code"]["params"][0].update(grid=[2, 3, 4]))
        r = self.run_py(BUILD, str(self.spec), "--out", str(self.out))
        self.assertIn("grid point 'k=4|boost=1.0' missing", r.stdout)

    def test_earlier_method_needs_code_or_reason(self):
        self.edit(lambda d: d["features"][0].pop("prior_code"))
        r = self.run_py(BUILD, str(self.spec), "--out", str(self.out))
        self.assertIn("n/a: reason", r.stdout)

    def test_reimplementation_needs_parity(self):
        res = self.dir / "results/f1.json"
        d = json.loads(res.read_text())
        d["provenance"] = "AI re-implementation"
        res.write_text(json.dumps(d))
        r = self.run_py(BUILD, str(self.spec), "--out", str(self.out))
        self.assertIn("parity", r.stdout)

    def test_check_rejects_external_resources_stale_code_and_tracked_output(self):
        self.assertEqual(self.run_py(BUILD, str(self.spec), "--out", str(self.out)).returncode, 0)
        self.out.write_text(self.out.read_text().replace("<head>", '<head><script src="https://cdn.example/x.js"></script>'))
        code = self.dir / "code/method.py"
        code.write_text(code.read_text().replace("edges = []", "edges = list()"))
        ws = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(ws)], check=True)
        c = self.run_py(CHECK, str(self.spec), str(self.out), "--workspace", str(ws))
        self.assertEqual(c.returncode, 1)
        self.assertIn("external resource", c.stdout)
        self.assertIn("differs from the current source", c.stdout)
        self.assertIn("not ignored", c.stdout)
    def test_storyline_layer_is_checked_before_units_exist(self):
        outline = SKILL / "scripts/check_outline.py"
        ok = self.run_py(outline, str(self.spec))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.edit(lambda d: d["difficulties"].append({"id": "3", "title": "x", "text": "y"}))
        r = self.run_py(outline, str(self.spec))
        self.assertEqual(r.returncode, 1)
        self.assertIn("difficulty 3: no step answers it", r.stdout)
        self.edit(lambda d: d["overview"][0].update(answers=["9"]))
        r = self.run_py(outline, str(self.spec))
        self.assertIn("not a difficulty id", r.stdout)
        self.edit(lambda d: d["overview"][0].pop("why"))
        r = self.run_py(outline, str(self.spec))
        self.assertIn("missing why", r.stdout)

    def test_check_finds_duplicate_ids_and_dead_links_in_the_rendered_page(self):
        sys.path.insert(0, str(SKILL / "scripts"))
        import check_companion
        if not check_companion.find_chrome():
            self.skipTest("no Chrome/Chromium for the rendered-page check")
        self.assertEqual(self.run_py(BUILD, str(self.spec), "--out", str(self.out)).returncode, 0)
        good = self.run_py(CHECK, str(self.spec), str(self.out))
        self.assertEqual(good.returncode, 0, good.stdout)
        self.out.write_text(self.out.read_text().replace("</body>", '<a href="#nowhere">x</a><p id="top"></p></body>'))
        bad = self.run_py(CHECK, str(self.spec), str(self.out))
        self.assertEqual(bad.returncode, 1)
        self.assertIn('id "top" appears 2 times', bad.stdout)
        self.assertIn("#nowhere points to no element", bad.stdout)


if __name__ == "__main__":
    unittest.main()
