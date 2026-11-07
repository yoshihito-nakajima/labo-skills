#!/usr/bin/env python3
"""Structural checks for a built proof-review page.

Usage: check_review_page.py PAGE.html [--spec SPEC_DIR] [--katex-dir DIR]

Always checks: no unreplaced placeholders, unique ids, every internal #link resolves, and (with
--spec) that every ledger step and finding has a card. When node and KaTeX are available it also
parses every math span and the page scripts; otherwise it says that part was skipped. This does not
look at the screen: open the page in a browser (or a headless one) and read it as well.
"""
import argparse
import collections
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_review_page import find_katex  # noqa: E402

NODE_MATH = r"""
const fs=require('fs');const [,,page,kjs]=process.argv;
const html=fs.readFileSync(page,'utf8');const katex=require(kjs);
const body=html.split('<main>')[1].split('</main>')[0];
const dec=s=>s.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
let n=0,bad=0;const re=/<span class="m">([\s\S]*?)<\/span>|<div class="d">([\s\S]*?)<\/div>/g;let m;
while((m=re.exec(body))){const t=dec((m[1]||m[2]).replace(/<[^>]+>/g,''));n++;
 try{katex.renderToString(t,{throwOnError:true,displayMode:!!m[2]});}catch(e){bad++;console.log('BAD MATH',t.slice(0,80),'|',e.message.slice(0,60));}}
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]).slice(1);
scripts.forEach((s,i)=>{try{new Function(s)}catch(e){bad++;console.log('BAD SCRIPT',i,e.message)}});
console.log('math spans',n,'bad',bad);process.exit(bad?1:0);
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("page")
    ap.add_argument("--spec")
    ap.add_argument("--katex-dir")
    a = ap.parse_args(argv)
    page = pathlib.Path(a.page).read_text(encoding="utf-8")
    errors, notes = [], []
    if re.search(r"\{\{[A-Za-z_:]+\}\}", page):
        errors.append("unreplaced {{placeholder}} in page")
    ids = re.findall(r'\bid="([^"]+)"', page)
    for k, c in collections.Counter(ids).items():
        if c > 1:
            errors.append(f"duplicate id {k}")
    for h in sorted(set(re.findall(r'href="#([^"]+)"', page))):
        if h not in ids:
            errors.append(f"link #{h} has no target")
    if a.spec:
        spec = pathlib.Path(a.spec)
        for s in json.load(open(spec / "steps.json", encoding="utf-8"))["steps"]:
            tgt = json.load(open(spec / "steps.json", encoding="utf-8")).get("_meta", {}).get("target", "T")
            if s["id"] != tgt and f"step-{s['id']}" not in ids:
                errors.append(f"no card for step {s['id']}")
        for f in json.load(open(spec / "review.json", encoding="utf-8"))["findings"]:
            if f"find-{f['id']}" not in ids:
                errors.append(f"no card for finding {f['id']}")
    kdir = find_katex(a.katex_dir)
    if shutil.which("node") and kdir:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as t:
            t.write(NODE_MATH)
        r = subprocess.run(["node", t.name, str(pathlib.Path(a.page).resolve()), str(kdir / "katex.min.js")], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode:
            errors.append("math or script syntax errors (see above)")
    else:
        notes.append("math/script syntax check skipped (needs node and a KaTeX directory)")
    for e in errors:
        print("ERROR", e)
    for n in notes:
        print("NOTE", n)
    if not errors:
        print("page structure OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
