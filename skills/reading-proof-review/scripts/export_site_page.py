#!/usr/bin/env python3
"""Export a proof-review spec as a private Reader page for the site generator.

Usage:
  export_site_page.py SPEC_DIR --slug SLUG --out-dir CONTENT_DIR [--lang ja|en]

This is the *site route* for a proof-review reading (see labo-layout, "Private HTML"): the same
spec directory that `build_review_page.py` turns into a standalone HTML page is written as
authored Markdown, `CONTENT_DIR/SLUG.md`, and the dependency diagram as
`CONTENT_DIR/figures/SLUG/diagram.svg`. CONTENT_DIR is the generator's private content directory
(`website/content/private`). Use one route or the other for a given page, not both.

The generator must support nested `::: details Summary {#anchor}` blocks, pipe tables, `$...$` and
`$$...$$` mathematics and `![alt](asset:diagram.svg)` figures.
"""
import argparse
import datetime
import html as htmllib
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_ledger  # noqa: E402
import indicator  # noqa: E402
from build_review_page import LABELS, SEV_ORDER, diagram  # noqa: E402


def esc(text):
    """Escape plain text for Markdown prose (mathematics is written by the caller)."""
    text = str(text).replace("\\", "\\\\")
    for ch in "*_`":
        text = text.replace(ch, "\\" + ch)
    return text


def cell(text):
    return re.sub(r"\s+", " ", esc(text)).replace("|", "\\|").strip() or "—"


class _ToMarkdown(HTMLParser):
    """Convert the small HTML subset used in spec fields into Markdown."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.math = None  # None, or (kind, [chunks])
        self.lists = []

    def _break(self):
        text = "".join(self.out)
        if text and not text.endswith("\n\n"):
            self.out.append("\n" if text.endswith("\n") else "\n\n")

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag == "span" and cls == "m":
            self.math = ("inline", [])
        elif tag == "div" and cls == "d":
            self._break()
            self.math = ("display", [])
        elif tag in ("p", "div"):
            self._break()
        elif tag in ("b", "strong"):
            self.out.append("**")
        elif tag in ("i", "em"):
            self.out.append("*")
        elif tag == "code":
            self.out.append("`")
        elif tag in ("ul", "ol"):
            self._break()
            self.lists.append([tag, 0])
        elif tag == "li":
            if self.out and not "".join(self.out).endswith("\n"):
                self.out.append("\n")
            depth = max(len(self.lists) - 1, 0)
            kind = self.lists[-1] if self.lists else ["ul", 0]
            kind[1] += 1
            marker = f"{kind[1]}." if kind[0] == "ol" else "-"
            self.out.append("   " * depth + marker + " ")
        elif tag == "br":
            self.out.append("  \n")

    def handle_endtag(self, tag):
        if tag == "span" and self.math and self.math[0] == "inline":
            self.out.append("$" + "".join(self.math[1]).strip() + "$")
            self.math = None
        elif tag == "div" and self.math and self.math[0] == "display":
            self.out.append("$$\n" + "".join(self.math[1]).strip() + "\n$$\n\n")
            self.math = None
        elif tag in ("p", "div"):
            self._break()
        elif tag in ("b", "strong"):
            self.out.append("**")
        elif tag in ("i", "em"):
            self.out.append("*")
        elif tag == "code":
            self.out.append("`")
        elif tag in ("ul", "ol"):
            if self.lists:
                self.lists.pop()
            self._break()
        elif tag == "li":
            self.out.append("\n")

    def handle_data(self, data):
        if self.math is not None:
            self.math[1].append(data)
        else:
            self.out.append(esc(data))


def md(fragment):
    if not fragment:
        return ""
    parser = _ToMarkdown()
    parser.feed(fragment)
    parser.close()
    text = "".join(parser.out)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def details(summary, anchor, body):
    head = f"::: details {summary}" + (f" {{#{anchor}}}" if anchor else "")
    return f"{head}\n\n{body.strip()}\n\n:::"


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def export(spec_dir, lang, slug):
    L = LABELS[lang]
    spec = pathlib.Path(spec_dir)
    meta, steps = check_ledger.load(spec / "steps.json")
    target = meta.get("target", "T")
    errors, _ = check_ledger.check(meta, steps)
    if errors:
        raise SystemExit("ledger errors:\n" + "\n".join(errors))
    bodies = json.load(open(spec / "bodies.json", encoding="utf-8"))
    R = json.load(open(spec / "review.json", encoding="utf-8"))
    S = {s["id"]: s for s in steps}
    F = {f["id"]: f for f in R["findings"]}
    by_step = {}
    for f in R["findings"]:
        for st in f.get("steps", []):
            if st not in S:
                raise SystemExit(f"finding {f['id']} refers to unknown step {st}")
            by_step.setdefault(st, []).append(f["id"])
    tier_name = {k: L["tier_" + k] for k in ("key", "semi", "standard")}
    origin_name = {k: L["origin_" + k] for k in check_ledger.ORIGINS}

    def link(i):
        return esc(i) if i == target else f"[{esc(i)}](#step-{i})"  # the target has no step block of its own

    def status_text(f):
        return f.get("status_note") or L["st_" + f["status"]]

    parts = []
    title = R["title"].replace("\\", "\\\\").replace('"', '\\"')
    front = f'+++\ntitle = "{title}"\nslug = "{slug}"\nlanguage = "{lang}"\n+++\n'
    sub = R.get("subtitle", "")
    parts.append(f"> {esc(L['caution'])}\n>\n> {L['generated']} {datetime.date.today().isoformat()}")
    if sub:
        parts.append(esc(sub))

    parts.append(f"## {L['h_summary']}\n\n{md(R['summary_html'])}")
    if R.get("intro_html"):
        parts.append(f"## {L['h_intro']}\n\n{md(R['intro_html'])}")

    spine = []
    if R.get("key_ideas_html"):
        spine.append("\n".join("> " + line for line in md(R["key_ideas_html"]).splitlines()))
    hint = re.sub(r"[^。.]*(クリック|[Cc]lick)[^。.]*[。.]?\s*$", "", L["diagram_hint"]).strip()  # a figure is an image: its boxes are not links
    spine.append(f"### {L['h_diagram']}\n\n{esc(hint)}\n\n![{L['h_diagram']}](asset:diagram.svg)")
    lead = re.sub(r"[^。.]*(キーは|Key steps)[^。.]*[。.]?\s*$", "", L["spine_lead"]).strip()  # folds start closed here
    spine.append(esc(lead))
    groups = R.get("groups") or [["", [s["id"] for s in steps if s["id"] != target]]]
    grouped = {i for _, ids in groups for i in ids}
    rest = [s["id"] for s in steps if s["id"] != target and s["id"] not in grouped]
    if rest:
        groups = groups + [["", rest]]
    for gtitle, ids in groups:
        if gtitle:
            spine.append(f"### {esc(gtitle)}")
        for i in ids:
            s, b = S[i], bodies.get(i, {})
            flags = "".join(f" ［{x}］" for x in by_step.get(i, []))
            deps = "、".join(link(x) for x in s["deps"]) or L["none"]
            inner = [f"{L['meta_loc']}: {esc(s['loc'])}　/　{L['meta_origin']}: {origin_name[s['origin']]}　/　{L['meta_deps']}: {deps}",
                     md(b.get("l1")) or esc(s["statement"])]
            if s.get("why_tier"):
                inner.append(f"{L['why_tier']}: {esc(s['why_tier'])}")
            if b.get("l2"):
                inner.append(details(L["l2"], None, md(b["l2"])))
            if b.get("l3"):
                inner.append(details(L["l3"], None, md(b["l3"])))
            if by_step.get(i):
                items = "\n".join(f"- [{x}](#find-{x})　{esc(F[x]['short'])}" for x in by_step[i])
                inner.append(details(L["step_findings"] % len(by_step[i]), None, items))
            summary = f"［{tier_name[s['tier']]}］{esc(i)}　{esc(s['title'])}{flags}"
            spine.append(details(summary, "step-" + i, "\n\n".join(inner)))
    parts.append(f"## {L['h_spine']}\n\n" + "\n\n".join(spine))

    sr = R.get("step_review", {})
    rows = []
    for t in ("key", "semi", "standard"):
        for s in steps:
            if s["id"] == target or s["tier"] != t:
                continue
            r = sr.get(s["id"], {})
            rows.append([f"{tier_name[t]} {s['id']}", s["title"], s.get("role", ""), origin_name[s["origin"]], r.get("risk", "—"), r.get("evidence", "—")])
    comp = [esc(L["compare_lead"]),
            table([L["th_class"], L["th_content"], L["th_role"], L["th_origin"], L["th_risk"], L["th_evidence"]], rows)]
    if R.get("compare_note_html"):
        comp.append(md(R["compare_note_html"]))
    parts.append(f"## {L['h_compare']}\n\n" + "\n\n".join(comp))

    cnt = {k: sum(1 for f in R["findings"] if f["sev"] == k) for k in SEV_ORDER}
    rev = [f"**{L['review_conclusion']}**　{esc(R['review_conclusion'])}",
           esc(L["n_findings"] % (len(R["findings"]), cnt["fatal"], cnt["major"], cnt["minor"], cnt["form"])),
           f"**{L['review_reading']}**　{esc(L['review_reading_text'])}",
           f"### {L['h_panel']}",
           table([L["th_view"], L["th_who"], L["th_scope"], L["th_result"]], [[p["name"], p["who"], p["scope"], p["result"]] for p in R["panel"]])]
    if R.get("my_checks"):
        rev.append(f"### {L['h_mychecks']}\n\n" + "\n".join(f"- {esc(x)}" for x in R["my_checks"]))
    rev.append(f"### {L['h_findings']}\n\n{esc(L['findings_hint'])}")
    for f in sorted(R["findings"], key=lambda f: (SEV_ORDER[f["sev"]], f["id"])):
        st = "、".join(link(x) for x in f.get("steps", [])) or L["f_all"]
        body = [f"{L['f_target']}: {st}　/　{L['f_from']}: {esc('、'.join(f['from']))}", md(f["detail"])]
        for k1, k2 in (("evidence", "f_evidence"), ("ruling", "f_ruling")):
            if f.get(k1):
                body.append(f"{L[k2]}: {esc(f[k1])}")
        rev.append(details(f"［{L['sev_' + f['sev']]}／{esc(status_text(f))}］{esc(f['id'])}　{esc(f['short'])}", "find-" + f["id"], "\n\n".join(body)))
    parts.append(f"## {L['h_review']}\n\n" + "\n\n".join(rev))

    pr = [table([L["th_prior"], L["th_op"], L["th_hyp"], L["th_overlap"], L["th_state"]],
                [[p["name"], p["op"], p["hyp"], p["overlap"], p["state"]] for p in R["prior"]])]
    if R.get("prior_hole"):
        pr.append(f"**{L['prior_hole']}**　{esc(R['prior_hole'])}")
    if R.get("uncited"):
        pr.append(f"### {L['prior_uncited']}\n\n" + "\n".join(f"- {esc(x)}" for x in R["uncited"]))
    if R.get("admitted"):
        pr.append(f"### {L['prior_admitted']}\n\n" + "\n".join(f"- {esc(x)}" for x in R["admitted"]))
    parts.append(f"## {L['h_prior']}\n\n" + "\n\n".join(pr))

    ind = R["indicator"]
    violations = indicator.violations(ind)
    if violations:
        raise SystemExit("indicator violates the rules:\n" + "\n".join(violations))
    axes = f"### {L['axes_h']}\n\n" + "\n".join(f"- **{L['ax_' + a['key']]}**（{L['lvl_' + a['level']]}）{esc(a['why'])}" for a in ind["axes"])
    parts.append(f"## {L['h_indicator']}\n\n**{L['verdict']}: {L['v_' + ind['verdict']]}**　{esc(ind['verdict_why'])}\n\n{axes}\n\n"
                 f"### {L['rules_h']}\n\n" + "\n".join(f"- {esc(r)}" for r in indicator.RULES[lang])
                 + f"\n\n### {L['changers_h']}\n\n" + "\n".join(f"{n}. {esc(c)}" for n, c in enumerate(ind["changers"], 1))
                 + f"\n\n> {esc(L['indicator_note'])}")
    if R.get("glossary"):
        parts.append(f"## {L['h_glossary']}\n\n" + "\n".join(f"- **{md(g[0])}**：{md(g[1])}" for g in R["glossary"]))

    svg = diagram(steps, target, by_step)
    svg = svg.replace("<svg ", '<svg width="100%" ', 1)
    return front + "\n" + "\n\n".join(parts) + "\n", svg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec_dir")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out-dir", required=True, help="the generator's private content directory (website/content/private)")
    ap.add_argument("--lang", default="ja", choices=sorted(LABELS))
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", a.slug):
        raise SystemExit("slug must be lowercase ASCII letters, digits and single hyphens")
    page, svg = export(a.spec_dir, a.lang, a.slug)
    out = pathlib.Path(a.out_dir)
    fig = out / "figures" / (a.slug[:-3] if a.slug.endswith("-en") else a.slug)
    fig.mkdir(parents=True, exist_ok=True)
    (out / f"{a.slug}.md").write_text(page, encoding="utf-8")
    (fig / "diagram.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {out / (a.slug + '.md')} and {fig / 'diagram.svg'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
