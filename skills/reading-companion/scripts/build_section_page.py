#!/usr/bin/env python3
"""Build the section-structured page and the matching TeX parts from one section record.

Usage:
  build_section_page.py RECORD.json --out DIR [--base BASE] [--original PDF]

Writes DIR/index.html (collapsed hierarchy, single file), DIR/panels/p<ID>.tex (section head
panels), DIR/codecards/c<ID>.tex (Steps and comparison cards) and DIR/overview.tex. Code
paths in the record are relative to BASE (default: the record's directory). With --original,
sections that give `heading_word` get the original page region (heading to next heading) as an
embedded image beside the translation file `translation_html` (optional, a path to an HTML
fragment). See references/section-page.md and reading-reference/references/survey-profile.md.
Needs only the standard library; pandoc (math to MathML), pdftotext and pdftoppm are used when present.
"""
import argparse, base64, html, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

KIND = {"author": "author", "official": "official", "lib": "library", "ai": "AI stand-in", "none": "none"}
STATUS = {"same": ("same", "same"), "changed": ("changed", "chg"), "only_left": ("only left", "onl"), "only_right": ("only right", "onl")}
MATSTATE = {"held": "held", "alt": "alternative only", "req": "requested", "requested": "requested", "paid": "paid", "na": "n/a"}
HAVE_PANDOC = shutil.which("pandoc") is not None


def esc(s): return html.escape(str(s))


def m(s):
    """Text with $...$ math to HTML (MathML through pandoc when available)."""
    if not s: return ""
    if "$" not in s or not HAVE_PANDOC: return esc(s)
    r = subprocess.run(["pandoc", "-f", "latex", "-t", "html", "--mathml"], input=s, capture_output=True, text=True)
    t = r.stdout.strip()
    return re.sub(r"^<p>|</p>$", "", t) if r.returncode == 0 and t else esc(s)


def tx(s):
    out = []
    for p in re.split(r"(\$[^$]*\$)", str(s or "")):
        out.append(p if p.startswith("$") else p.replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("#", r"\#").replace("&", r"\&").replace("%", r"\%"))
    return "".join(out)


class Rec:
    def __init__(self, path, base=None):
        self.d = json.load(open(path, encoding="utf-8"))
        self.base = Path(base) if base else Path(path).resolve().parent
        self.S = self.d["sections"]
        self.BY = {s["id"]: s for s in self.S}
        self.FIGS = self.d.get("figures", {})
        self.edges = {}
        for a, b, w in self.d.get("edges", []): self.edges.setdefault((a, b), w)

    def anc(self, i):
        out, p = [], self.BY[i].get("parent")
        while p: out.append(p); p = self.BY[p].get("parent")
        return out

    def kids(self, i): return [s for s in self.S if s.get("parent") == i]

    def edges_of(self, i, key):
        res = []
        for (a, b), w in self.edges.items():
            if key == "recv" and b == i and a not in self.anc(i) and i not in self.anc(a): res.append((a, w))
            if key == "pas" and a == i and b not in self.anc(i) and i not in self.anc(b): res.append((b, w))
        return res

    def lines(self, f, a, b):
        return (self.base / f).read_text(encoding="utf-8").split("\n")[a - 1:b]


def badge(k): return f'<span class="by by-{k}">{esc(KIND.get(k, k))}</span>'
def pages(s): a, b = s["pages"]; return f"p.{a}" if a == b else f"pp.{a}–{b}"


def code_box(R, x, cls=""):
    if not x: return '<pre class="cb none">(not on this side)</pre>'
    if isinstance(x, dict) and "lit" in x: return f'<pre class="cb {cls}"><span class="ln">—</span> {esc(x["lit"])}</pre>'
    f, a, b = x
    body = "\n".join(f'<span class="ln">{a + i}</span> {esc(l)}' for i, l in enumerate(R.lines(f, a, b)))
    return f'<pre class="cb {cls}">{body}</pre><div class="muted small">{esc(f)} {a}–{b}</div>'


def nlines(x): return 0 if (not x or isinstance(x, dict)) else x[2] - x[1] + 1


def summary(cmp):
    rows = cmp["rows"]; tot = sum(nlines(r.get("right")) for r in rows)
    c = {k: sum(nlines(r.get("right")) for r in rows if r["status"] == k) for k in ("same", "changed", "only_right")}
    return f'Of the {tot} right-hand lines compared, {c["same"]} are the same, {c["changed"]} changed, {c["only_right"]} only on the right.'


def panel_html(R, s):
    i = s["id"]; rows = []
    def row(k, v): rows.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
    ch = [k["id"] for k in R.kids(i)]
    row("Position", " ＞ ".join([f'<a href="#sec-{a}">§{a}</a>' for a in R.anc(i)[::-1]] + [f"§{i}"]) + ("  sections: " + ", ".join(f'<a href="#sec-{c}">§{c}</a>' for c in ch) if ch else ""))
    row("Question", m(s["question"])); row("Answer", m(s["answer"])); row("Evidence", m(s["evidence"])); row("Selling point", m(s.get("sell", "")))
    row("Receives", "<br>".join(f'<a href="#sec-{a}">§{a}</a> {m(w)}' for a, w in R.edges_of(i, "recv")) or "—")
    row("Hands on", "<br>".join(f'<a href="#sec-{b}">§{b}</a> {m(w)}' for b, w in R.edges_of(i, "pas")) or "—")
    if s.get("figures"):
        row("Figures", "<br>".join(f'<a href="#fig-{f}">{esc(f)}</a> (p.{R.FIGS[f]["page"]}): {m(R.FIGS[f]["what"])} <span class="muted">colour: {m(R.FIGS[f]["color"])}</span>' for f in s["figures"]))
    cd = [c for c in s.get("code", []) if c.get("kind") != "none"]
    row("Code", "<br>".join(f'{badge(c["kind"])} <b>{esc(c["name"])}</b> {esc(c.get("src", ""))} <span class="muted">[{esc(c.get("state", ""))}]</span>' for c in cd) or "no code in this section")
    row("Materials", "<br>".join(f'{esc(x["item"])}: <span class="mat {esc(x["state"])}">{esc(MATSTATE.get(x["state"], x["state"]))}</span> <span class="muted">{esc(x.get("note", ""))}</span>' for x in s.get("materials", [])) or "—")
    return f'<div class="panel2"><table>{"".join(rows)}</table></div>'


def card_html(R, s):
    out = [f'<p>Steps below show verbatim lines; the math correspondence follows each code block.</p>']
    if s.get("flow"): out.append(f'<div class="flow"><b>What this code solves (overall flow)</b><p>{m(s["flow"])}</p></div>')
    for st in s["steps"]:
        ln = "".join(f'<tr><td class="small">line {a}</td><td>{m(b)}</td></tr>' for a, b in st.get("lines", []))
        ap = "".join(f'<div class="apic"><b><code>{esc(x["name"])}</code></b> <code class="small">{esc(x.get("sig", ""))}</code><br><b>returns:</b> {m(x.get("ret", ""))}<br><b>note:</b> {m(x.get("note", ""))}' + (f'<br><b>cost:</b> {m(x["cost"])}' if x.get("cost") else "") + (f'<div class="small muted">{esc(x["quote"])}</div>' if x.get("quote") else "") + '</div>' for x in st.get("apis", []))
        out.append(f'<div class="step"><h4>{esc(st["title"])}</h4><p>{m(st["what"])}</p>{code_box(R, (st["file"], st["first"], st["last"]))}'
                   + (f'<div class="lines"><b>Reading the lines</b><table>{ln}</table></div>' if ln else "")
                   + (f'<details class="blk"><summary>Functions used in this Step ({len(st["apis"])})</summary><div class="inner">{ap}</div></details>' if ap else "")
                   + f'<p class="mapto"><b>Math:</b> {m(st["math"])}</p></div>')
    if s.get("after"): out.append(f'<div class="flow after"><b>Meaning of the result, and where it leads</b><p>{m(s["after"])}</p></div>')
    cm = s.get("comparison")
    if cm:
        body = ""
        for r in cm["rows"]:
            lab, cls = STATUS[r["status"]]
            body += (f'<div class="cmprow {cls}"><div><span class="stl {cls}">{lab}</span> <b>{esc(r["label"])}</b>: {m(r["why"])}</div><div class="cmpgrid">'
                     f'<div><div class="side">Left: {m(cm["left"]["name"])}</div>{code_box(R, r.get("left"), cls if r.get("left") else "")}</div>'
                     f'<div><div class="side">Right: {m(cm["right"]["name"])}</div>{code_box(R, r.get("right"), cls if r.get("right") else "")}</div></div></div>')
        pr = "".join("<tr>" + "".join(f"<td>{m(c)}</td>" for c in row) + "</tr>" for row in cm.get("params", []))
        out.append(f'<div class="cmpcard"><h3>{m(cm["title"])}</h3><p><b>{summary(cm)}</b></p>{body}<h4>Parameters</h4><table><tr><th>argument</th><th>left</th><th>right</th><th>effect</th></tr>{pr}</table><p class="small">{m(cm.get("note", ""))}</p></div>')
    else:
        out.append(f'<div class="cmpcard none"><b>No comparison.</b> {m(s.get("no_comparison_reason", ""))}</div>')
    return "".join(out)


# --- original region (optional) ---
def locate(words, sid, first, a, b):
    for p in range(a, b + 2):
        ws = words.get(p, [])
        for k in range(len(ws) - 1):
            if ws[k][2] == sid and ws[k][0] < 140 and ws[k + 1][2] == first: return (p, ws[k][1])
    return None


def read_words(pdf):
    x = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True).stdout
    words = {}
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', x, re.S):
        words[len(words) + 1] = [(float(a), float(b), html.unescape(w)) for a, b, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">(.*?)</word>', pm.group(3))]
    return words


def crops(R, s, pdf, words):
    order = [x["id"] for x in R.S]; k = order.index(s["id"])
    st = locate(words, s["id"], s.get("heading_word", ""), *s["pages"])
    nxt = R.BY[order[k + 1]] if k + 1 < len(order) else None
    nx = locate(words, nxt["id"], nxt.get("heading_word", ""), *nxt["pages"]) if nxt else None
    if not st: return [], "heading not located; showing whole pages"
    en = nx or (st[0], 800); out = []; sc = 110 / 72
    for p in range(st[0], en[0] + 1):
        y0 = st[1] - 6 if p == st[0] else 70; y1 = en[1] - 6 if p == en[0] else 790
        if y1 - y0 < 14: continue
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["pdftoppm", "-r", "110", "-f", str(p), "-l", str(p), "-x", "60", "-y", str(int(y0 * sc)), "-W", str(int(480 * sc)), "-H", str(int((y1 - y0) * sc)), "-jpeg", str(pdf), d + "/x"], check=True, capture_output=True)
            fn = sorted(os.listdir(d))[0]
            out.append((p, "data:image/jpeg;base64," + base64.b64encode(open(d + "/" + fn, "rb").read()).decode()))
    return out, f"from the heading of §{s['id']} on p.{st[0]} to the next heading"


def orig_html(R, s, pdf, words):
    tr = ""
    if s.get("translation_html"): tr = (R.base / s["translation_html"]).read_text(encoding="utf-8")
    elif s.get("translation"): tr = "".join(f"<p>{m(p)}</p>" for p in s["translation"])
    imgs, desc = ([], "")
    if pdf and s.get("heading_word"): imgs, desc = crops(R, s, pdf, words)
    left = "".join(f'<figure><img src="{u}" alt="p.{p}"><figcaption>p.{p} (original, this section only)</figcaption></figure>' for p, u in imgs) or '<p class="muted">no original region (give --original and heading_word)</p>'
    return f'<div class="otgrid"><div><h4>Original</h4><p class="small muted">{esc(desc)}</p>{left}</div><div><h4>Faithful translation</h4>{tr or "<p class=muted>(none)</p>"}</div></div>'


CSS = """body{font-family:system-ui,sans-serif;max-width:1200px;margin:0 auto;padding:0 1rem;line-height:1.5}details.blk{border:1px solid #cdd;border-radius:6px;margin:.5rem 0}details.blk>summary{cursor:pointer;padding:.4rem .7rem;font-weight:600;background:#f3f6f8}.inner{padding:.5rem .8rem}
.panel2 table{width:100%;border-collapse:collapse}.panel2 th{width:8rem;text-align:left;vertical-align:top;font-size:.85rem;color:#055}.by{font-size:.72rem;padding:0 .35rem;border-radius:3px;margin-right:.2rem;background:#eee}.by-author,.by-official{background:#d8f0dc}.by-lib{background:#e3eaf8}.by-ai{background:#fbe3d0}
.cb{background:#fbfbfd;border:1px solid #dde;padding:.3rem .5rem;font-size:.78rem;overflow:auto;white-space:pre}.cb .ln{color:#999;margin-right:.5rem}.cb.same{background:#eef8ee}.cb.chg{background:#fff8dc}.cb.onl{background:#eaf1fb}.cb.none{color:#999}.step{border-left:3px solid #9bc;padding:0 .6rem;margin:.6rem 0}.cmprow{margin:.5rem 0;padding:.3rem .5rem;border-radius:4px}
.cmprow.same{background:#f2faf2}.cmprow.chg{background:#fffbe9}.cmprow.onl{background:#f1f6fc}.cmpgrid,.otgrid{display:grid;grid-template-columns:1fr 1fr;gap:.6rem}.otgrid img{max-width:100%;border:1px solid #ccd}.stl{font-size:.75rem;padding:0 .4rem;border-radius:3px;font-weight:700}.stl.same{background:#bfe3c1}.stl.chg{background:#f3dd7c}.stl.onl{background:#b9d0ee}.muted{color:#777}.small{font-size:.85rem}
.lead,.bridge,.flow{background:#f7fbf9;border-left:4px solid #6b9;padding:.4rem .8rem;margin:.5rem 0}.bridge,.flow.after{border-left-color:#c96;background:#fcf9f5}.apic{border:1px solid #dde;padding:.3rem .5rem;margin:.3rem 0;font-size:.88rem}.lines td{border:1px solid #eee;padding:.1rem .4rem}.figin{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.figin img{max-width:100%}@media(max-width:900px){.cmpgrid,.otgrid,.figin{grid-template-columns:1fr}}"""


def section_html(R, s, pdf, words):
    i = s["id"]; parts = [f'<details class="blk" id="p-{i}" open><summary>Section structure</summary><div class="inner">{panel_html(R, s)}</div></details>']
    if s.get("explanation_html"): parts.append(f'<details class="blk" id="ex-{i}"><summary>Explanation</summary><div class="inner">{(R.base / s["explanation_html"]).read_text(encoding="utf-8")}</div></details>')
    if s.get("glossary"):
        gl = "".join(f'<tr><td><b>{m(w)}</b></td><td>{m(d)}</td><td class="small">{esc(wh)}</td><td class="small">{esc(fl)}</td></tr>' for w, d, wh, fl in s["glossary"])
        parts.append(f'<details class="blk" id="gl-{i}"><summary>Terms in this section ({len(s["glossary"])})</summary><div class="inner"><table><tr><th>term</th><th>plain explanation and what it is good for</th><th>where</th><th>field</th></tr>{gl}</table></div></details>')
    parts.append(f'<details class="blk" id="ot-{i}"><summary>Original and faithful translation ({pages(s)})</summary><div class="inner">{orig_html(R, s, pdf, words)}</div></details>')
    if s.get("figures"):
        fig = ""
        for f in s["figures"]:
            d = R.FIGS[f]; img = f'<img src="{esc(d["image"])}" alt="{esc(f)}">' if d.get("image") else ""
            rel = "".join(f'<li>{esc(a)} → {esc(b)}: <b>{esc(k)}</b>. {m(dd)}</li>' for a, b, k, dd in R.d.get("figure_links", []) if f in (a, b))
            fig += f'<div class="figin"><div>{img}</div><div><h4>{esc(f)} (p.{d["page"]})</h4><p>{m(d["what"])}</p><p>{m(d.get("text", ""))}</p><p><b>Colour:</b> {m(d["color"])}</p>{"<ul>" + rel + "</ul>" if rel else ""}</div></div>'
        parts.append(f'<details class="blk"><summary>Figures of this section</summary><div class="inner">{fig}</div></details>')
    if s.get("steps"): parts.append(f'<details class="blk" id="cu-{i}"><summary>Code: Steps and comparison</summary><div class="inner">{card_html(R, s)}</div></details>')
    if s.get("ledger_html"): parts.append(f'<details class="blk" id="led-{i}"><summary>Math ledger of this section</summary><div class="inner">{s["ledger_html"]}</div></details>')
    kids = "".join(section_html(R, k, pdf, words) for k in R.kids(i))
    bridge = f'<div class="bridge"><b>To the next section</b><p>{m(s["bridge"])}</p></div>' if s.get("bridge") else ""
    w = " ".join(f"{n}{v}" for n, v in zip(("math", "code", "fig"), s.get("weights", [0, 0, 0])))
    kinds = " ".join(badge(c["kind"]) for c in s.get("code", []) if c.get("kind") != "none")
    return (f'<details class="blk" id="sec-{i}"><summary>§{i} {esc(s["title"])} <span class="muted small">{pages(s)} {w}</span> {kinds}'
            f'<div class="small" style="font-weight:400">{m(s.get("sell", ""))}</div></summary><div class="inner">{"".join(parts)}{kids}{bridge}</div></details>')


def build_html(R, pdf=None):
    words = read_words(pdf) if pdf else {}
    secs = "".join(section_html(R, s, pdf, words) for s in R.S if not s.get("parent"))
    ov = "<ol>" + "".join(f'<li>§{s["id"]} <b>{esc(s["title"])}</b>: {m(s["question"])} → {m(s["answer"])}</li>' for s in R.S if not s.get("parent")) + "</ol>"
    frows = "".join(f'<tr id="fig-{esc(f)}"><td>{esc(f)}</td><td>p.{d["page"]}</td><td>{m(d["what"])}</td><td>{m(d["color"])}</td></tr>' for f, d in R.FIGS.items())
    crow = "".join(f'<tr><td><a href="#sec-{s["id"]}">§{s["id"]}</a></td><td>{esc(c["name"])}</td><td>{badge(c["kind"])}</td><td>{esc(c.get("src", ""))}</td><td>{esc(c.get("state", ""))}</td><td>{esc(c.get("lic", ""))}</td></tr>' for s in R.S for c in s.get("code", []) if c.get("kind") != "none")
    def top(i, t, b, op=False): return f'<details class="blk" id="{i}"{" open" if op else ""}><summary>{t}</summary><div class="inner">{b}</div></details>'
    body = (top("overview", "1 Overview", ov, True) + top("figs", "2 Figure list", f"<table><tr><th>figure</th><th>page</th><th>content</th><th>colour legend</th></tr>{frows}</table>")
            + top("codes", "3 Code list", f"<table><tr><th>section</th><th>code</th><th>kind</th><th>source</th><th>state</th><th>licence</th></tr>{crow}</table>")
            + top("ledger", "3' Ledger (concepts, claims)", R.d.get("ledger_html", "<p class=muted>(attach the ledger here)</p>"))
            + top("secs", "4 Sections", secs) + top("appx", "5 Appendix", R.d.get("appendix_html", "<p class=muted>materials, acquisition state, request list</p>")))
    js = "<script>addEventListener('hashchange',function(){var e=document.getElementById(location.hash.slice(1));while(e){if(e.tagName==='DETAILS')e.open=true;e=e.parentElement}});</script>"
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(R.d.get("title", ""))}</title><style>{CSS}</style></head><body><h1>{esc(R.d.get("title", ""))}</h1><p class="small muted">{esc(R.d.get("source", ""))}. Private page; do not publish.</p>{body}{js}</body></html>'


# --- TeX ---
def lst(R, x, tag, litdir):
    if not x: return r"\par{\small\itshape (not on this side)}"
    if isinstance(x, dict):
        litdir.mkdir(parents=True, exist_ok=True); (litdir / f"{tag}.txt").write_text(x["lit"] + "\n"); return r"\lstinputlisting[numbers=none]{%s}" % (litdir / f"{tag}.txt")
    f, a, b = x; lang = "Matlab" if f.endswith(".m") else "Python"
    return r"\lstinputlisting[language=%s,firstline=%d,lastline=%d,firstnumber=%d]{%s}\par{\scriptsize %s %d--%d}" % (lang, a, b, a, R.base / f, tx(f), a, b)


def card_tex(R, s, litdir):
    L = [r"\par\medskip\noindent{\large\bfseries \S%s Code: Steps%s}\par" % (s["id"], " and comparison" if s.get("comparison") else " (no comparison)")]
    if s.get("flow"): L.append(r"\par{\small\textbf{What this code solves.} %s}\par" % tx(s["flow"]))
    for st in s["steps"]:
        L += [r"\par\smallskip\noindent\textbf{%s}\quad %s\par" % (tx(st["title"]), tx(st["what"])), lst(R, (st["file"], st["first"], st["last"]), "", litdir)]
        if st.get("lines"): L.append(r"\par{\small\textbf{Reading the lines}}\begin{itemize}\footnotesize" + "".join(r"\item line %s: %s" % (a, tx(b)) for a, b in st["lines"]) + r"\end{itemize}")
        if st.get("apis"): L.append(r"\par{\small\textbf{Functions used}}\begin{itemize}\footnotesize" + "".join(r"\item \texttt{%s}\ \texttt{%s}: returns %s; note: %s%s" % (tx(x["name"]), tx(x.get("sig", "")), tx(x.get("ret", "")), tx(x.get("note", "")), (r" {\scriptsize %s}" % tx(x["quote"])) if x.get("quote") else "") for x in st["apis"]) + r"\end{itemize}")
        L.append(r"\par{\small\textbf{Math:} %s}\par" % tx(st["math"]))
    if s.get("after"): L.append(r"\par{\small\textbf{Meaning of the result.} %s}\par" % tx(s["after"]))
    cm = s.get("comparison")
    if cm:
        L.append(r"\par\medskip\noindent\textbf{%s}\par{\small %s}\par" % (tx(cm["title"]), tx(summary(cm))))
        clr = {"same": "green!12", "chg": "yellow!25", "onl": "blue!10"}
        for n, r in enumerate(cm["rows"]):
            lab, cls = STATUS[r["status"]]; tag = f"{s['id'].replace('.', '_')}_{n}"
            L.append(r"\begin{tcolorbox}[colback=%s,boxrule=0.3pt,fontupper=\small]\textbf{[%s] %s:} %s\par\noindent\begin{minipage}[t]{0.485\linewidth}%s\end{minipage}\hfill\begin{minipage}[t]{0.485\linewidth}%s\end{minipage}\end{tcolorbox}" % (clr[cls], lab, tx(r["label"]), tx(r["why"]), lst(R, r.get("left"), tag + "_L", litdir), lst(R, r.get("right"), tag + "_R", litdir)))
        L.append(r"\par{\small %s}" % tx(cm.get("note", "")))
    else:
        L.append(r"\par{\small\textbf{No comparison.} %s}" % tx(s.get("no_comparison_reason", "")))
    return "\n".join(L)


def panel_tex(R, s):
    rows = [("Question", tx(s["question"])), ("Answer", tx(s["answer"])), ("Evidence", tx(s["evidence"])), ("Selling point", tx(s.get("sell", ""))),
            ("Receives", "; ".join(f"\\S{a} {tx(w)}" for a, w in R.edges_of(s["id"], "recv")) or "--"), ("Hands on", "; ".join(f"\\S{b} {tx(w)}" for b, w in R.edges_of(s["id"], "pas")) or "--")]
    for f in s.get("figures", []): rows.append(("Figure", f"{tx(f)} (p.{R.FIGS[f]['page']}): {tx(R.FIGS[f]['what'])} / colour: {tx(R.FIGS[f]['color'])}"))
    cd = [c for c in s.get("code", []) if c.get("kind") != "none"]
    rows.append(("Code", "; ".join(f"[{KIND.get(c['kind'], c['kind'])}] {tx(c['name'])}" for c in cd) or "none"))
    head = r"{\small\bfseries Section structure: \S%s %s (%s)}" % (s["id"], tx(s["title"]), pages(s))
    body = "".join(f"{k} & {v} \\\\[2pt]\n" for k, v in rows)
    lead = (r"\par\medskip\noindent{\small\textbf{Entrance.} %s}\par" % tx(s["lead"])) if s.get("lead") else ""
    return (lead + r"\par\medskip\noindent\begin{tcolorbox}[colback=black!2,boxrule=0.4pt,fontupper=\small]" + head + r"\par\smallskip\begin{tabular}{@{}>{\raggedright\bfseries}p{2.4cm}@{\hspace{4pt}}>{\raggedright\arraybackslash}p{12.6cm}@{}}" + body + r"\end{tabular}\end{tcolorbox}\par\medskip")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("record"); ap.add_argument("--out", required=True); ap.add_argument("--base"); ap.add_argument("--original")
    a = ap.parse_args(argv)
    R = Rec(a.record, a.base); out = Path(a.out); (out / "panels").mkdir(parents=True, exist_ok=True); (out / "codecards").mkdir(exist_ok=True)
    (out / "index.html").write_text(build_html(R, a.original), encoding="utf-8")
    for s in R.S:
        (out / "panels" / f"p{s['id']}.tex").write_text(panel_tex(R, s) + "\n")
        if s.get("steps"): (out / "codecards" / f"c{s['id']}.tex").write_text(card_tex(R, s, out / "lit") + "\n")
        if s.get("glossary"):
            (out / "glossary").mkdir(exist_ok=True)
            rows = "".join(f"{tx(w)} & {tx(d)} & {tx(wh)} & {tx(fl)} \\\\\n" for w, d, wh, fl in s["glossary"])
            (out / "glossary" / f"g{s['id']}.tex").write_text(r"{\footnotesize\begin{longtable}{@{}p{2.8cm}p{9.2cm}p{1.8cm}p{1.2cm}@{}}\toprule term&explanation and use&where&field\\\midrule\endhead" + "\n" + rows + r"\bottomrule\end{longtable}}" + "\n")
        if s.get("bridge"):
            (out / "bridge").mkdir(exist_ok=True); (out / "bridge" / f"br{s['id']}.tex").write_text(r"\par\medskip\noindent{\small\textbf{To the next section.} %s}\par" % tx(s["bridge"]) + "\n")
    print(f"built {len(R.S)} sections -> {out}")


if __name__ == "__main__":
    main()
