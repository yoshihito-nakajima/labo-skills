#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prototype: one derivation source -> a detailed PDF and an abridged HTML, linked formula by formula.

Source format (blocks/<ID>.txt), see D.txt:
  header   block: / title: / claim: / loc:          (key: value)
  step     step: D.1 / title: / ledger: / loc: / claim:
  prose    > text                shared text with $math$
  narr     >> text               narration: a paragraph that plans or recaps (HTML: muted, can be hidden)
  line     - TeX @@ lead @@ flags
             lead  = the clause printed BEFORE the formula, ending in a connective ("... なので、")
             flags = fine[:topic]  (shown only in the PDF; the HTML gives one explicit link row per run)
                     recon         (added by the page author, not in the manuscript; marked with a dagger)
Line ids are <step>.<n> over every '- ' line of the step. A line id written in any text ("(D.1.5)")
is a reference: that line then gets an automatic equation number; lines nobody refers to get none.
Numbers are never typed: the PDF uses \\label/\\eqref and the HTML computes the same numbers
(checked against the PDF's .aux after the build). A reference to a 'fine' line is refused: the HTML hides it.
"""
import argparse
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from build_review_page import LABELS, find_katex, katex_assets  # noqa: E402

E = html.escape
# Project state, filled by load_project(): blocks directory, ledger entries, context (problem, difficulties, roles, whys).
BLOCKS_DIR = pathlib.Path(".")
LEDGER = {}
CTX = {"page": {}, "diffs": {}, "block": {}, "step": {}}
PREFIX = "proof"

ID_LINE = re.compile(r"(?<![\w.])([A-Z]\.\d+\.\d+)(?![\w]|\.\d)")
ID_STEP = re.compile(r"(?<![\w.])([A-Z]\.\d+)(?![\w]|\.\d)")
REL = re.compile(r"\\leq(?![a-zA-Z])|\\geq(?![a-zA-Z])|\\le(?![a-zA-Z])|\\ge(?![a-zA-Z])|=|<|>")
STARTREL = re.compile(r"^\s*(\\leq(?![a-zA-Z])|\\geq(?![a-zA-Z])|\\le(?![a-zA-Z])|\\ge(?![a-zA-Z])|=|<|>)")
TEX_ESC = {"%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_"}


# ---------------------------------------------------------------- parse
def parse(path):
    blk = {"steps": [], "intro": []}
    cur = None
    for raw in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        if raw.startswith("step:"):
            cur = {"id": raw[5:].strip(), "items": [], "n": 0}
            blk["steps"].append(cur)
        elif raw.startswith(">> "):
            (cur["items"] if cur else blk["intro"]).append({"kind": "prose", "narr": True, "text": raw[3:].strip()})
        elif raw.startswith("> "):
            (cur["items"] if cur else blk["intro"]).append({"kind": "prose", "narr": False, "text": raw[2:].strip()})
        elif raw.startswith("- "):
            parts = [p.strip() for p in raw[2:].split(" @@ ")]
            if len(parts) < 2:
                raise SystemExit(f"line needs 'tex @@ lead': {raw[:60]}")
            cur["n"] += 1
            flags = {}
            for f in parts[2:]:
                k, _, v = f.partition(":")
                flags[k.strip()] = v.strip() or True
            cur["items"].append({"kind": "line", "id": f"{cur['id']}.{cur['n']}", "tex": parts[0], "lead": parts[1],
                                 "fine": "fine" in flags, "topic": flags.get("fine") if isinstance(flags.get("fine"), str) else "",
                                 "recon": "recon" in flags})
        else:
            k, _, v = raw.partition(":")
            (cur if cur else blk)[k.strip()] = v.strip()
    blk["id"] = blk.pop("block")
    return blk


def all_text(blk):
    ts = [blk.get("claim", "")] + [i["text"] for i in blk["intro"]]
    for st in blk["steps"]:
        ts.append(st.get("claim", ""))
        for it in st["items"]:
            ts.append(it["text"] if it["kind"] == "prose" else it["lead"])
    return ts


def numbering(blk):
    """Which lines are referenced, and the equation number each gets (same rule as the PDF's counters)."""
    lines = {it["id"]: it for st in blk["steps"] for it in st["items"] if it["kind"] == "line"}
    refs = set()
    for t in all_text(blk):
        text_only = "".join(seg for i, seg in enumerate(t.split("$")) if i % 2 == 0)
        refs.update(ID_LINE.findall(text_only))
    for r in refs:
        if r not in lines:
            raise SystemExit(f"reference to unknown line {r}")
        if lines[r]["fine"]:
            raise SystemExit(f"reference to hidden (fine) line {r}: the HTML does not show it")
    nums = {}
    for st in blk["steps"]:
        k = 0
        for it in st["items"]:
            if it["kind"] == "line" and it["id"] in refs:
                k += 1
                nums[it["id"]] = f"{st['id']}.{k}"
    return refs, nums


# ---------------------------------------------------------------- context (who uses whom)
TIER = {"key": "鍵", "semi": "準鍵", "standard": "標準"}
ORIGIN = {"inherited(LS)": "Li–Salgado から引き継ぎ", "standard": "標準", "adapted": "既存の手法の適用・一般化", "new": "原稿が新しいと主張"}


def usage():
    """step -> steps it cites ('uses') and steps that cite it ('used_by'), from every block source in blocks/."""
    uses, used_by = {}, {}
    for f in sorted(BLOCKS_DIR.glob("*.txt")):
        blk = parse(f)
        for st in blk["steps"]:
            texts = [st.get("claim", "")] + [i["text"] if i["kind"] == "prose" else i["lead"] for i in st["items"]]
            cited = []
            for t in texts:
                for seg in "".join(x for k, x in enumerate(t.split("$")) if k % 2 == 0).split("\n"):
                    cited += [f"{m.group(1)}.{m.group(2)}" for m in XBLOCK.finditer(seg) if m.group(2)]
                    cited += [m for m in ID_STEP.findall(seg) if m.startswith(blk["id"] + ".")]
            for c in dict.fromkeys(cited):
                if c != st["id"]:
                    uses.setdefault(st["id"], []).append(c)
                    used_by.setdefault(c, []).append(st["id"])
    return uses, used_by


def ledger_entry(lid):
    return LEDGER.get(lid)


def step_ctx_data(sid):
    d = CTX["step"].get(sid, {})
    return d.get("why", ""), d.get("diffs", [])


def block_ctx_data(bid):
    d = CTX["block"].get(bid, {})
    return d.get("role", ""), d.get("diffs", [])


def step_link(sid, here_block, merged):
    b = sid.split(".")[0]
    href = ("#%s" % sid) if (merged or b == here_block) else ("%s-block-%s.html#%s" % (PREFIX, b, sid))
    return '<a class="xb" href="%s">%s</a>' % (href, sid)


def diff_chips(ds, merged):
    base = "" if merged else "%s.html" % PREFIX
    return "".join('<a class="dchip" href="%s#diff-%d" title="%s">難所 %d</a>' % (base, n, E(CTX["diffs"][n]["title"]), n) for n in ds)


def step_ctx(st, here_block, merged, uses, used_by):
    why, ds = step_ctx_data(st["id"])
    led = ledger_entry(st.get("ledger", ""))
    cls = ""
    if led:
        cls = "%s・%s（暫定）" % (TIER.get(led.get("tier"), "?"), ORIGIN.get(led.get("origin"), "?"))
    rows = []
    if why:
        rows.append("<div><b>なぜここで要るか</b>　%s %s</div>" % (to_html(why), diff_chips(ds, merged)))
    if used_by.get(st["id"]):
        rows.append("<div><b>使われる先</b>　%s</div>" % "　".join(step_link(x, here_block, merged) for x in used_by[st["id"]]))
    if uses.get(st["id"]):
        rows.append("<div><b>前提にする段</b>　%s</div>" % "　".join(step_link(x, here_block, merged) for x in uses[st["id"]]))
    if cls:
        rows.append('<div class="lab"><b>分類</b>　台帳 %s：%s</div>' % (E(st.get("ledger", "")), E(cls)))
    return '<div class="ctx">%s</div>' % "".join(rows) if rows else ""


def block_ctx(blk, merged):
    role, ds = block_ctx_data(blk["id"])
    if not role:
        return ""
    return '<div class="card ctxb"><p><b>このブロックの役割</b>　%s　%s</p></div>' % (to_html(role), diff_chips(ds, merged))


# ---------------------------------------------------------------- text helpers
def tex_math(m):
    return re.sub(r"\\,d([st])(?![a-zA-Z])", r"\\,\\textup{d}\1", m)


USES, USED_BY = {}, {}
MERGED = False   # one combined page: links to other blocks are in-page anchors
XBLOCK = re.compile(r"ブロック ([A-Z])(?:・段 (\d+))?(?![A-Za-z])")   # other blocks, HTML only: "ブロック D・段 3"
ANY_LINE = re.compile(r"\(\s*([A-Z]\.\d+\.\d+)\s*\)|(?<![\w.])([A-Z]\.\d+\.\d+)(?![\w]|\.\d)")


def link_tex(t):
    t = ANY_LINE.sub(lambda m: r"\eqref{%s}" % (m.group(1) or m.group(2)), t)
    t = ID_STEP.sub(lambda m: r"\ref{%s}" % m.group(1), t)
    return XBLOCK.sub(lambda m: (r"\hyperref[%s.%s]{ブロック~%s・段~%s}" % (m.group(1), m.group(2), m.group(1), m.group(2))) if m.group(2)
                      else (r"\hyperref[blk-%s]{ブロック~%s}" % (m.group(1), m.group(1))), t)


def to_tex(s):
    segs = []
    for i, seg in enumerate(s.split("$")):
        if i % 2 == 0:
            segs.append(link_tex("".join(TEX_ESC.get(c, c) for c in seg)))
        else:
            segs.append("$" + tex_math(seg) + "$")
    return "".join(segs)


def to_html(s, nums=None):
    nums = nums or {}
    out = []
    for i, seg in enumerate(s.split("$")):
        if i % 2:
            out.append('<span class="m">%s</span>' % E(seg, quote=False))
            continue
        seg = E(seg)

        def eq(m):
            i = m.group(1) or m.group(2)
            return '<a href="#%s">(%s)</a>' % (i, nums.get(i, i))
        seg = ANY_LINE.sub(eq, seg)
        seg = ID_STEP.sub(lambda m: '<a href="#%s">%s</a>' % (m.group(1), m.group(1)), seg)
        seg = XBLOCK.sub(lambda m: '<a class="xb" href="%s%s">%s</a>' % ("" if MERGED else "%s-block-%s.html" % (PREFIX, m.group(1)), ("#%s.%s" % (m.group(1), m.group(2))) if m.group(2) else "#blk-%s" % m.group(1), m.group(0)), seg)
        out.append(seg)
    return "".join(out)


def split_at_relation(tex):
    depth, i = 0, 0
    while i < len(tex):
        c = tex[i]
        if c in "{([":
            depth += 1
        elif c in "})]":
            depth -= 1
        elif depth == 0:
            m = REL.match(tex, i)
            if m and (i == 0 or tex[i - 1] != "\\"):
                return tex[:i], tex[i:]
        i += 1
    return None


SPLITS = set()   # line ids that overflowed the page width in an earlier build: broken into one row per relation


def split_all(tex):
    """Top-level relation split: [head, '<rel>rhs', '<rel>rhs', ...] (head may be empty)."""
    depth, i, cuts = 0, 0, []
    while i < len(tex):
        c = tex[i]
        if c in "{([":
            depth += 1
        elif c in "})]":
            depth -= 1
        elif depth == 0:
            m = REL.match(tex, i)
            if m and (i == 0 or tex[i - 1] != "\\"):
                cuts.append(i)
                i = m.end()
                continue
        i += 1
    if not cuts:
        return [tex]
    pos = [0] + cuts + [len(tex)]
    parts = [tex[pos[k]:pos[k + 1]] for k in range(len(pos) - 1)]
    return parts if parts[0].strip() else parts[1:]


def chains(items):
    """Group consecutive line items into chains (a continuation line begins with a relation symbol)."""
    out, cur = [], []
    for it in items:
        if it["kind"] == "line" and cur and STARTREL.match(it["tex"]):
            cur.append(it)
            continue
        if cur:
            out.append(("chain", cur))
            cur = []
        if it["kind"] == "line":
            cur = [it]
        else:
            out.append(("prose", it))
    if cur:
        out.append(("chain", cur))
    return out


# ---------------------------------------------------------------- PDF (TeX)
def anchor_of(blk):
    """line id -> id of the HTML element that shows it (a fine run shares its first line's id)."""
    amap = {}
    for st in blk["steps"]:
        first = None
        for it in st["items"]:
            if it["kind"] != "line":
                first = None
                continue
            if it["fine"]:
                first = first or it["id"]
                amap[it["id"]] = first
            else:
                first = None
                amap[it["id"]] = it["id"]
    return amap


def render_chain(run, refs, html_path, amap):
    out = []
    if run[0]["lead"]:
        out.append(to_tex(run[0]["lead"]))
    rows = []
    for k, it in enumerate(run):
        t = tex_math(it["tex"]).replace("\\newrow", "\\notag\\\\\n&\\quad ")
        mark = (r"$^{\dagger}$" if it["recon"] else "") + ("細部" if it["fine"] else "")
        note = r"&&\text{\scriptsize %s\ \urilink{%s}{%s}{↗}\proofmark{%s}}" % (mark, html_path, amap[it["id"]], it["id"])
        num = ("\\label{%s}" % it["id"]) if it["id"] in refs else r"\notag"
        if it["id"] in SPLITS and "\\begin" not in t:
            parts = split_all(t)
            if k == 0 and len(parts) > 1 and not STARTREL.match(parts[0]):
                bodies = [parts[0] + "&" + parts[1]] + ["&" + q for q in parts[2:]]
            else:
                bodies = ["&" + q for q in parts] if STARTREL.match(parts[0]) else ["{}&" + "".join(parts)]
            pieces = [b + (r"\notag" if n < len(bodies) - 1 else note + num) for n, b in enumerate(bodies)]
            row = "\\\\\n".join(pieces)
        else:
            if k == 0:
                sp = split_at_relation(t)
                body = (sp[0] + "&" + sp[1]) if sp else "{}&" + t
            else:
                body = "&" + t
            row = "%s%s%s" % (body, note, num)
        if k > 0 and it["lead"]:
            rows.append("\\\\\n\\intertext{%s}\n%s" % (to_tex(it["lead"]), row))
        else:
            rows.append(("\\\\\n" if k > 0 else "") + row)
    out.append("\\begin{align}\n" + "".join(rows) + "\n\\end{align}")
    return "\n".join(out)


def plain(t):
    """Title for the table of contents and PDF bookmarks: no math, no markup."""
    return re.sub(r"\s+", " ", re.sub(r"\$[^$]*\$", "", t)).replace("（）", "").replace("[", "(").replace("]", ")").strip()


def ctx_tex(st, uses, used_by):
    why, ds = step_ctx_data(st["id"])
    led = ledger_entry(st.get("ledger", ""))
    rows = []
    if why:
        rows.append(r"\textbf{\textcolor{blue}{なぜここで要るか}}\quad %s %s\par" % (to_tex(why), "".join(r"\hyperref[diff-%d]{\textcolor{orange!70!black}{[難所~%d]}}~" % (n, n) for n in ds)))
    if used_by.get(st["id"]):
        rows.append(r"\textbf{\textcolor{blue}{使われる先}}\quad %s\par" % r"\quad ".join(r"\hyperref[%s]{%s}" % (x, x) for x in used_by[st["id"]]))
    if uses.get(st["id"]):
        rows.append(r"\textbf{\textcolor{blue}{前提にする段}}\quad %s\par" % r"\quad ".join(r"\hyperref[%s]{%s}" % (x, x) for x in uses[st["id"]]))
    if led:
        rows.append(r"\textbf{\textcolor{blue}{分類}}\quad 台帳 %s：%s・%s（暫定）\par" % (st.get("ledger", ""), TIER.get(led.get("tier"), "?"), ORIGIN.get(led.get("origin"), "?")))
    return (r"\begin{tcolorbox}[colback=blue!4,colframe=blue!25,boxrule=.4pt,left=5pt,right=5pt,top=2pt,bottom=2pt,breakable,fontupper=\small]" + "\n".join(rows) + r"\end{tcolorbox}") if rows else ""


def render_tex_all(blocks, html_path, refs, uses, used_by, order, title="証明"):
    """One PDF with the problem section and every block.  Sections carry the block id, steps <id>.n, equations <id>.n.k"""
    amap = {}
    for b in blocks:
        amap.update(anchor_of(b))
    L = []
    a = L.append
    a(r"""%% Generated by proofsrc.py from blocks/*.txt -- edit the sources, not this file.
%% A proof-centred reading PDF (not a paper): problem and difficulties first, then blocks A.. each with its role,
%% each step with its context box; reasons come BEFORE formulas; equation numbers and links are automatic and blue.
\documentclass[a4paper,11pt]{ltjsarticle}
\usepackage[margin=24mm]{geometry}
\usepackage{amsmath,amssymb,amsthm,mathtools,bm,xcolor}
\usepackage[most]{tcolorbox}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue,bookmarksnumbered=false,bookmarksopen=true,bookmarksopenlevel=2]{hyperref}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\allowdisplaybreaks[4]
\setlength{\abovedisplayskip}{4pt}\setlength{\belowdisplayskip}{3pt}\setlength{\abovedisplayshortskip}{4pt}\setlength{\belowdisplayshortskip}{3pt}\setlength{\jot}{5pt}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\numberwithin{equation}{subsection}
\setcounter{tocdepth}{2}
\makeatletter
\def\tagform@#1{\maketag@@@{\textcolor{blue}{(\ignorespaces#1\unskip\@@italiccorr)}}}
\renewcommand{\@seccntformat}[1]{\textcolor{blue}{\csname the#1\endcsname}\hskip 0.5em}
\makeatother
\newtheoremstyle{bluehead}{4pt}{4pt}{\itshape}{}{\bfseries\color{blue}}{.}{0.6em}{\thmname{#1}\thmnote{ \normalfont\color{black}(#3)}}
\theoremstyle{bluehead}\newtheorem*{lemma}{補題~\thesubsection}
\renewcommand{\proofname}{証明}
\makeatletter
\newcommand{\proofmark}[1]{\protected@write\@auxout{}{\string\proofpage{#1}{\thepage}}}
\makeatother
\providecommand{\proofpage}[2]{}
\begingroup\catcode`\#=12 \gdef\urihash{#}\endgroup
\newcommand{\urilink}[3]{{\color{blue!70!black}\pdfextension startlink attr {/Border[0 0 0]} user {/Subtype/Link/A<</S/URI/URI(file://\detokenize{#1}\urihash\detokenize{#2})>>}#3\pdfextension endlink}}
\begin{document}
""".replace("%%", "%"))
    a(r"{\LARGE\bfseries %s}\par" % to_tex(title))
    a(r"{\small 読むための PDF（論文の形ではない）。対応する HTML：\urilink{%s}{top}{HTML を開く}。式の右の「↗」は HTML の同じ式へ、HTML の「PDF ↗」はこの PDF の同じ式へ移る（同じフォルダに置いて使う）。リンクが開かないときは、HTML と PDF を同じフォルダに置いて開き直す。式の右の † は、原稿に無く、読解のために補った行。}\par" % html_path)
    a(r"\tableofcontents")
    a(r"\clearpage")
    a(r"\phantomsection\hypertarget{problem}{}\section*{この問題と、どこが難しいか}\addcontentsline{toc}{section}{この問題と、どこが難しいか}")
    for title, key in (("問題設定", "setting"), ("何を示すか", "goal")):
        a(r"\paragraph{\textcolor{blue}{%s}}" % title)
        for t in CTX["page"].get(key, []):
            a(to_tex(t) + r"\par")
    a(r"\paragraph{\textcolor{blue}{難所（素直にやると何が起きるか）}}")
    for n in sorted(CTX["diffs"]):
        blks = "、".join(r"\hyperref[blk-%s]{%s}" % (b, b) for b in order if n in CTX["block"].get(b, {}).get("diffs", []))
        a(r"\phantomsection\hypertarget{diff-%d}{}\label{diff-%d}" % (n, n))
        a(r"\begin{tcolorbox}[colback=orange!5,colframe=orange!35,boxrule=.4pt,left=5pt,right=5pt,top=2pt,bottom=2pt,breakable]\textbf{難所~%d：%s}\par %s\par{\small 受け持つブロック：%s}\end{tcolorbox}" % (n, to_tex(CTX["diffs"][n]["title"]), to_tex(CTX["diffs"][n]["text"]), blks))
    a(r"\paragraph{\textcolor{blue}{戦略（原稿が主張する工夫）}}")
    for t in CTX["page"].get("strategy", []):
        a(to_tex(t) + r"\par")
    for blk in blocks:
        role, ds = block_ctx_data(blk["id"])
        a(r"\clearpage")
        a(r"\renewcommand{\thesection}{%s}" % blk["id"])
        a(r"\section[%s]{%s\hfill{\normalfont\small\urilink{%s}{blk-%s}{↗ HTML}}}" % (plain(blk["title"]), to_tex(blk["title"]), html_path, blk["id"]))
        a(r"\phantomsection\hypertarget{blk-%s}{}\label{blk-%s}\label{%s}" % (blk["id"], blk["id"], blk["id"]))
        a(r"{\small 原稿：%s}\par" % to_tex(blk.get("loc", "")))
        if role:
            a(r"\begin{tcolorbox}[colback=blue!4,colframe=blue!25,boxrule=.4pt,left=5pt,right=5pt,top=2pt,bottom=2pt,fontupper=\small]\textbf{\textcolor{blue}{このブロックの役割}}\quad %s %s\end{tcolorbox}" % (to_tex(role), "".join(r"\hyperref[diff-%d]{\textcolor{orange!70!black}{[難所~%d]}}~" % (n, n) for n in ds)))
        a(r"\textbf{主張}\quad " + to_tex(blk["claim"]) + r"\par")
        for it in blk["intro"]:
            a(to_tex(it["text"]) + r"\par")
        for st in blk["steps"]:
            a(r"\bigskip")
            a(r"\subsection[%s]{%s\hfill{\normalfont\small\urilink{%s}{%s}{↗ HTML}}}" % (plain(st["title"]), to_tex(st["title"]), html_path, st["id"]))
            a(r"\phantomsection\hypertarget{%s}{}\label{%s}" % (st["id"], st["id"]))
            a(ctx_tex(st, uses, used_by))
            a(r"{\small 原稿：%s}\par" % to_tex(st.get("loc", "")))
            a(r"\begin{lemma}")
            a(to_tex(st["claim"]))
            a(r"\end{lemma}")
            a(r"\begin{proof}")
            for kind, payload in chains(st["items"]):
                if kind == "prose":
                    a(to_tex(payload["text"]) + r"\par")
                else:
                    a(render_chain(payload, refs, html_path, amap))
            a(r"\end{proof}")
    a(r"\end{document}")
    return "\n".join(L) + "\n"


def parse_aux(aux_path):
    """id -> (displayed number or None, page)"""
    txt = pathlib.Path(aux_path).read_text(encoding="utf-8")
    out = {}
    pat = re.compile(r"\\newlabel\{([^}]+)\}\{\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}\{(\d+)\}")
    for m in pat.finditer(txt):
        out[m.group(1)] = (re.sub(r"[{}]", "", m.group(2)), int(m.group(3)))
    for m in re.finditer(r"\\proofpage\{([^}]+)\}\{(\d+)\}", txt):
        num = out.get(m.group(1), (None,))[0]
        out[m.group(1)] = (num, int(m.group(2)))
    return out


# ---------------------------------------------------------------- HTML
CSS = """<style>
main{max-width:1000px !important}
.eq{margin:.7em 0 .9em;scroll-margin-top:90px}
.eq .lead{margin:0 0 .1em;line-height:1.75}
.eq .fm{display:flex;align-items:center;justify-content:space-between;gap:1em;padding-left:1.6em}
.eq .fm .d{flex:1;overflow-x:auto;padding:0}
.eq .fm .katex-display{margin:.15em 0 !important;text-align:left}
.eq .fm .katex-display>.katex{text-align:left !important}
.eq .eqno{color:#1f5fbf;white-space:nowrap}
.eq .pdfi{font-size:12px;color:#8a93a3;text-decoration:none;white-space:nowrap;margin-left:.6em}
.eq .pdfi:hover{color:#1f5fbf;text-decoration:underline}
.eq .tg{font-size:12px;color:#c2410c;margin-left:.4em}
.eq.flash,.fine.flash{outline:3px solid #1f5fbf;outline-offset:6px;border-radius:4px}
.fine{margin:.6em 0;padding:.5em .9em;background:#fff7e6;border:1px dashed #e7c98f;border-radius:8px;font-size:14.5px}
.ctx{margin:.5em 0 .6em;padding:.45em .8em;background:#f3f7fd;border:1px solid #d5e2f6;border-radius:8px;font-size:14px;line-height:1.7}
.ctxb{background:#f3f7fd}
.dchip{display:inline-block;margin-left:.3em;padding:0 7px;border-radius:10px;background:#fde8d8;color:#a14a0c;font-size:12px;text-decoration:none}
body.hide-ctx .ctx{display:none}
.xb{color:#7a3fb0;text-decoration:none;border-bottom:1px dotted #7a3fb0}
.pdfl{display:inline-block;padding:0 8px;border:1px solid #bcd2f3;border-radius:6px;background:#e8f0fc;font-size:13px;text-decoration:none;color:#1f5fbf}
p.narr{background:#fbfbf4;border-left:4px solid #e3e2c8;padding:.45em .9em;margin:.9em 0;font-size:15px;color:#33405a}
body.hide-narr p.narr{display:none}
p.prose{margin:.8em 0}
</style>"""


def render_html(blk, pdf_name, aux, refs, nums, lang="ja", embed=False):
    Lb = LABELS[lang]
    amap = anchor_of(blk)
    page_of = {k: v[1] for k, v in aux.items()}

    def pl(i, label):
        p = page_of.get(i)
        return '<a class="pdfl" href="%s">%s</a>' % (f"{pdf_name}#page={p}" if p else pdf_name, label)

    topnav = '' if embed else '<p class="lab"><a href="%s.html#blk-%s">↩ 全体版（1 ページ）へ</a>　<a href="%s-index.html">↩ 索引へ</a></p>' % (PREFIX, blk["id"], PREFIX)
    body = [topnav + '<%s id="blk-%s">%s　%s</%s>' % ("h2" if embed else "h1", blk["id"], E(blk["id"]), to_html(blk["title"], nums), "h2" if embed else "h1"),
            '<p class="sub">%s<br><span class="lab">完全版の PDF：%s　同じフォルダに置いて使う。各式の「PDF ↗」は、PDF の同じ式のページへ移る。</span></p>' % (to_html(blk.get("loc", ""), nums), pl(blk["id"], "PDF を開く"))]
    body.append(block_ctx(blk, embed or MERGED))
    body.append('<div class="card key"><p><b>主張</b>　%s</p></div>' % to_html(blk["claim"], nums))
    for it in blk["intro"]:
        body.append('<p class="%s">%s</p>' % ("narr" if it.get("narr") else "prose", to_html(it["text"], nums)))
    for st in blk["steps"]:
        sid = st["id"]
        body.append('<details class="step t-keyc" id="%s" open><summary><span class="tag t-key">%s</span><b>%s</b>　%s</summary>' % (E(sid), E(st.get("ledger", "")), E(sid), to_html(st["title"], nums)))
        body.append(step_ctx(st, blk["id"], embed or MERGED, USES, USED_BY))
        body.append('<div class="meta">原稿：%s　/　%s</div>' % (to_html(st.get("loc", ""), nums), pl(sid, "↗ PDF の %s（p.%s）" % (sid, page_of.get(sid, "?")))))
        body.append('<div class="l1"><b>主張</b>　%s</div>' % to_html(st["claim"], nums))
        lhs = None  # left side of the current chain: continuation rows are aligned under its relation sign
        items = st["items"]
        for idx, it in enumerate(items):
            if it["kind"] == "prose":
                body.append('<p class="%s">%s</p>' % ("narr" if it.get("narr") else "prose", to_html(it["text"], nums)))
                lhs = None
                continue
            if it["fine"]:
                if idx > 0 and items[idx - 1]["kind"] == "line" and items[idx - 1]["fine"]:
                    continue  # rest of a run: already summarised by its first line
                j = idx
                while j < len(items) and items[j]["kind"] == "line" and items[j]["fine"]:
                    j += 1
                grp = items[idx:j]
                first = grp[0]["id"]
                topic = grp[0]["topic"] or "細部"
                body.append('<div class="fine" id="%s">▸ ここに <b>%d 行</b>（%s）が入る。長いので PDF だけに書いてある：%s</div>' % (E(first), len(grp), E(topic), pl(first, "PDF の該当の式（p.%s）" % page_of.get(first, "?"))))
                lhs = None
                continue
            t = it["tex"].replace("\\newrow", "\\;")
            if STARTREL.match(t) and lhs is not None:
                formula = r"\begin{aligned}\phantom{%s}&%s\end{aligned}" % (lhs, t)
            else:
                sp = split_at_relation(t)
                if sp:
                    lhs = sp[0]
                    formula = r"\begin{aligned}%s&%s\end{aligned}" % (sp[0], sp[1])
                else:
                    lhs = None
                    formula = t
            num = ('<span class="eqno">(%s)</span>' % nums[it["id"]]) if it["id"] in nums else ""
            dag = '<span class="tg" title="原稿に書かれておらず、読解版で補った行">†補足</span>' if it["recon"] else ""
            p = page_of.get(it["id"])
            pdfi = '<a class="pdfi" href="%s" title="PDF の同じ式のページへ">PDF ↗</a>' % (f"{pdf_name}#page={p}" if p else pdf_name)
            lead = '<div class="lead">%s%s</div>' % (to_html(it["lead"], nums), dag) if it["lead"] else ""
            body.append('<div class="eq" id="%s">%s<div class="fm"><div class="d">%s</div>%s%s</div></div>' % (E(it["id"]), lead, E(formula, quote=False), num, pdfi))
        body.append("</details>")
    if embed:
        return body
    script = """<script>(function(){
var nav=document.getElementById('nav');
var box=document.createElement('div');box.className='ctl2';
box.innerHTML='<b>説明の文章</b><button id="narr">隠す / 表示</button><b>文脈の欄</b><button id="ctxb">隠す / 表示</button>';nav.appendChild(box);document.getElementById('ctxb').onclick=function(){document.body.classList.toggle('hide-ctx');};
document.getElementById('narr').onclick=function(){document.body.classList.toggle('hide-narr');};
function openTo(id){var t=document.getElementById(id);if(!t)return;var p=t;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}
t.scrollIntoView({block:'center'});t.classList.add('flash');setTimeout(function(){t.classList.remove('flash');},2500);}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(a){e.preventDefault();openTo(a.getAttribute('href').slice(1));}});
if(location.hash){openTo(decodeURIComponent(location.hash.slice(1)));}
})();</script>"""
    tpl = (SKILL / "assets/review-page-template.html").read_text(encoding="utf-8")
    # the template's generic svg rule (border, width:100%) breaks KaTeX's own svg (radical signs)
    tpl = tpl.replace("svg{width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:8px}", "")
    kdir = find_katex()
    css, js, _ = katex_assets(kdir)
    page = (tpl.replace("{{BODY}}", CSS + "\n".join(body)).replace("{{TITLE}}", E(blk["title"])).replace("{{LANG}}", lang)
            .replace("{{EXTRA_SCRIPT}}", script).replace("/*KATEX_CSS*/", css).replace("/*KATEX_JS*/", js))
    return re.sub(r"\{\{L:([a-z_]+)\}\}", lambda m: E(Lb[m.group(1)]), page)


# ---------------------------------------------------------------- driver
def overfull_ids(src_dir):
    """Line ids of the display rows that the last LaTeX run reported as overfull (> 3pt)."""
    log = next(src_dir.rglob("*main.log")).read_text(errors="ignore")
    tex = (src_dir / "main.tex").read_text(encoding="utf-8").splitlines()
    ids = set()
    for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\) detected at line (\d+)", log):
        if float(m.group(1)) < 3:
            continue
        n = int(m.group(2)) - 1
        lo = n
        while lo > 0 and "\\begin{align}" not in tex[lo]:
            lo -= 1
        hi = n
        while hi < len(tex) - 1 and "\\end{align}" not in tex[hi]:
            hi += 1
        ids.update(re.findall(r"\\proofmark\{([^}]*)\}", "\n".join(tex[lo:hi + 1])))
    return ids




# ---------------------------------------------------------------- project and drivers
def load_project(project):
    """Read book.json, the block sources, the ledger and context.json of a project directory."""
    global BLOCKS_DIR, PREFIX
    project = pathlib.Path(project).resolve()
    cfg = json.loads((project / "book.json").read_text(encoding="utf-8"))
    BLOCKS_DIR = project / cfg.get("blocks_dir", "blocks")
    PREFIX = cfg.get("prefix", "proof")
    led = project / cfg.get("ledger", "ledger/steps.json")
    LEDGER.clear()
    if led.exists():
        LEDGER.update({x["id"]: x for x in json.loads(led.read_text(encoding="utf-8"))["steps"]})
    cp = project / cfg.get("context", "context.json")
    raw = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
    CTX["page"] = raw.get("page", {})
    CTX["diffs"] = {int(k): v for k, v in raw.get("diffs", {}).items()}
    CTX["block"] = raw.get("block", {})
    CTX["step"] = raw.get("step", {})
    out = project / cfg.get("out", "out")
    out.mkdir(parents=True, exist_ok=True)
    return cfg, out


def latex_build(src_dir, builder):
    """Compile src_dir/main.tex; return the PDF path.  builder: 'latexmk' (default) or a command template with {tex}."""
    env = {**os.environ, "TEXMFVAR": str(src_dir / ".texcache"), "TEXMFCACHE": str(src_dir / ".texcache")}
    (src_dir / ".texcache").mkdir(exist_ok=True)
    if builder == "latexmk":
        cmd = ["latexmk", "-lualatex", "-interaction=nonstopmode", "-halt-on-error", "-outdir=" + str(src_dir / ".temp"), str(src_dir / "main.tex")]
    else:
        cmd = [c.replace("{tex}", str(src_dir / "main.tex")) for c in builder.split()]
    r = subprocess.run(cmd, cwd=src_dir, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-1200:], r.stderr[-600:])
        raise SystemExit("LaTeX build failed")
    return src_dir / ".temp" / "main.pdf"


def overfull_ids_in(tex_path, log_path):
    log = pathlib.Path(log_path).read_text(errors="ignore")
    tex = pathlib.Path(tex_path).read_text(encoding="utf-8").splitlines()
    ids = set()
    for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\) detected at line (\d+)", log):
        if float(m.group(1)) < 3:
            continue
        n = int(m.group(2)) - 1
        lo = n
        while lo > 0 and "\\begin{align}" not in tex[lo]:
            lo -= 1
        hi = n
        while hi < len(tex) - 1 and "\\end{align}" not in tex[hi]:
            hi += 1
        ids.update(re.findall(r"\\proofmark\{([^}]*)\}", "\n".join(tex[lo:hi + 1])))
    return ids


def _page(body, title, extra_script=""):
    global MERGED
    tpl = (SKILL / "assets/review-page-template.html").read_text(encoding="utf-8")
    # the template's generic svg rule (border, width:100%) breaks KaTeX's own svg (radical signs)
    tpl = tpl.replace("svg{width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:8px}", "")
    css, js, _ = katex_assets(find_katex())
    page = (tpl.replace("{{BODY}}", body).replace("{{TITLE}}", E(title)).replace("{{LANG}}", "ja")
            .replace("{{EXTRA_SCRIPT}}", extra_script).replace("/*KATEX_CSS*/", css).replace("/*KATEX_JS*/", js))
    return re.sub(r"\{\{L:([a-z_]+)\}\}", lambda m: E(LABELS["ja"][m.group(1)]), page)


NAV_SCRIPT = """<script>(function(){
var nav=document.getElementById('nav');
var box=document.createElement('div');box.className='ctl2';
box.innerHTML='<b>説明の文章</b><button id="narr">隠す / 表示</button><b>文脈の欄</b><button id="ctxb">隠す / 表示</button>';nav.appendChild(box);
document.getElementById('ctxb').onclick=function(){document.body.classList.toggle('hide-ctx');};
document.getElementById('narr').onclick=function(){document.body.classList.toggle('hide-narr');};
function openTo(id){var t=document.getElementById(id);if(!t)return;var p=t;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}
t.scrollIntoView({block:'center'});t.classList.add('flash');setTimeout(function(){t.classList.remove('flash');},2500);}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(a){e.preventDefault();var id=decodeURIComponent(a.getAttribute('href').slice(1));history.replaceState(null,'','#'+id);openTo(id);}});
setTimeout(function(){document.querySelectorAll('#problem details').forEach(function(d){d.open=true;});},60);
if(location.hash){openTo(decodeURIComponent(location.hash.slice(1)));}
})();</script>"""


def write_combined(blocks, order, pdf_name, aux, per, title, out):
    global MERGED
    MERGED = True
    body = ['<h1 id="top">%s</h1>' % E(title),
            '<p class="sub">全ブロックを 1 ページに並べた版。左の目次、または下の一覧から各ブロックへ移れる。各式の「PDF ↗」は、そのブロックの PDF の同じ式へ移る（PDF は同じフォルダに置いて使う）。他のブロックを引く箇所は、このページの中で移る。</p>']
    chips = '<a class="pdfl" href="#blk-problem">この問題と難所</a>　' + "　".join('<a class="pdfl" href="#blk-%s">%s %s</a>' % (b["id"], b["id"], E(b["title"])) for b in blocks)
    body.append('<div class="card"><p><b>ブロック</b>　%s</p><p class="lab">読む順序は %s。</p></div>' % (chips, " → ".join(order)))
    if CTX["page"] or CTX["diffs"]:
        sec = ['<section class="blk" id="problem"><h2 id="blk-problem">この問題と、どこが難しいか</h2>']
        for head, key in (("問題設定", "setting"), ("何を示すか", "goal")):
            if CTX["page"].get(key):
                sec.append("<details open><summary><b>%s</b></summary>%s</details>" % (head, "".join('<p class="prose">%s</p>' % to_html(t) for t in CTX["page"][key])))
        if CTX["diffs"]:
            cards = "".join(
                '<div class="card" id="diff-%d"><p><b>難所 %d：%s</b></p><p>%s</p><p class="lab">受け持つブロック：%s</p></div>' % (
                    n, n, E(d["title"]), to_html(d["text"]),
                    "　".join('<a class="xb" href="#blk-%s">%s</a>' % (b, b) for b in order if n in CTX["block"].get(b, {}).get("diffs", [])))
                for n, d in sorted(CTX["diffs"].items()))
            sec.append("<details open><summary><b>難所（素直にやると何が起きるか）</b></summary>%s</details>" % cards)
        if CTX["page"].get("strategy"):
            sec.append("<details open><summary><b>戦略</b></summary>%s</details>" % "".join('<p class="prose">%s</p>' % to_html(t) for t in CTX["page"]["strategy"]))
        sec.append("</section>")
        body.append("\n".join(sec))
    for i, blk in enumerate(blocks):
        refs, nums = per[blk["id"]]
        part = render_html(blk, pdf_name, aux, refs, nums, embed=True)
        prev = '<a href="#blk-%s">← %s</a>' % (order[i - 1], order[i - 1]) if i else ""
        nxt = '<a href="#blk-%s">%s →</a>' % (order[i + 1], order[i + 1]) if i < len(order) - 1 else ""
        bar = '<p class="lab blkbar">%s　<a href="#top">↑ 先頭へ</a>　<a href="%s-index.html">索引</a>　%s</p>' % (prev, PREFIX, nxt)
        body.append('<section class="blk">' + bar + "\n".join(part) + bar + "</section>")
    css = "\n<style>.blk{margin:2.5em 0;padding-top:1em;border-top:3px solid #c9d6ee}.blkbar a{margin-right:.6em}</style>\n"
    (out / f"{PREFIX}.html").write_text(_page(CSS + css + "\n".join(body), title, NAV_SCRIPT), encoding="utf-8")
    MERGED = False


def write_index(blocks, pdf_name, pages, title, out):
    body = ['<h1>%s：ブロックの索引</h1>' % E(title),
            '<p class="sub">各ブロックは、1 つの HTML（主要な道筋）と、全体で 1 つの PDF（式変形をすべて書いた完全版）にある。全ブロックを 1 ページにした版は <a class="pdfl" href="%s.html">%s.html</a>（先頭に <a class="pdfl" href="%s.html#blk-problem">この問題と難所</a> の節がある）。</p>' % (PREFIX, PREFIX, PREFIX)]
    for blk in blocks:
        b = blk["id"]
        lines = [it for st in blk["steps"] for it in st["items"] if it["kind"] == "line"]
        html_name = f"{PREFIX}-block-{b}.html"
        steps = "".join('<li><a href="%s#%s">%s</a>　%s　<a class="pdfl" href="%s#page=%s">PDF p.%s</a></li>' % (
            html_name, st["id"], st["id"], to_html(st["title"]), pdf_name, pages.get(st["id"], 1), pages.get(st["id"], "?")) for st in blk["steps"])
        role = CTX["block"].get(b, {}).get("role", "")
        body.append('<div class="card"><h2>%s　%s</h2>%s<p><b>主張</b>　%s</p><ul>%s</ul><p><a class="pdfl" href="%s">HTML を開く</a>　<a class="pdfl" href="%s#page=%s">PDF の該当ページ</a><span class="lab">　式 %d 行（うち PDF だけ %d 行、原稿に無く補った行 %d 行）</span></p></div>' % (
            b, to_html(blk["title"]), ('<p class="lab">%s</p>' % to_html(role)) if role else "", to_html(blk["claim"]), steps,
            html_name, pdf_name, pages.get("blk-" + b, 1), len(lines), sum(1 for x in lines if x["fine"]), sum(1 for x in lines if x["recon"])))
    (out / f"{PREFIX}-index.html").write_text(_page(CSS + "\n".join(body), title + "：索引"), encoding="utf-8")


def build(project, builder=None):
    cfg, out = load_project(project)
    order = cfg["order"]
    title = cfg.get("title", "証明")
    blocks = [parse(BLOCKS_DIR / f"{b}.txt") for b in order]
    uses, used_by = usage()
    USES.update(uses); USED_BY.update(used_by)
    refs, nums, per = set(), {}, {}
    for b in blocks:
        r, n = numbering(b)
        refs |= r; nums.update(n); per[b["id"]] = (r, n)
    src_dir = out / ".tex"
    src_dir.mkdir(exist_ok=True)
    html_path = str((out / f"{PREFIX}.html").resolve())
    SPLITS.clear()
    for _ in range(5):
        (src_dir / "main.tex").write_text(render_tex_all(blocks, html_path, refs, uses, used_by, order, title), encoding="utf-8")
        for _ in range(2):  # twice: contents and references
            pdf = latex_build(src_dir, builder or cfg.get("builder", "latexmk"))
        wide = overfull_ids_in(src_dir / "main.tex", src_dir / ".temp" / "main.log")
        new = wide - SPLITS
        if not new:
            if wide:
                print("WARNING: still too wide after splitting:", sorted(wide))
            break
        print("too wide -> one row per relation:", sorted(new))
        SPLITS.update(new)
    aux = parse_aux(src_dir / ".temp" / "main.aux")
    bad = [(k, nums[k], aux.get(k, ("?",))[0]) for k in nums if aux.get(k, ("?",))[0] != nums[k]]
    if bad:
        raise SystemExit(f"HTML and PDF equation numbers differ: {bad[:6]}")
    for b in order:
        if "blk-" + b in aux:
            aux[b] = aux["blk-" + b]
    pdf_name = f"{PREFIX}.pdf"
    shutil.copy(pdf, out / pdf_name)
    pages = {k: v[1] for k, v in aux.items()}
    json.dump(pages, open(out / "pages.json", "w"), indent=0)
    for b in blocks:
        r, n = per[b["id"]]
        (out / f"{PREFIX}-block-{b['id']}.html").write_text(render_html(b, pdf_name, aux, r, n), encoding="utf-8")
    write_combined(blocks, order, pdf_name, aux, per, title, out)
    write_index(blocks, pdf_name, pages, title, out)
    print(f"equations numbered: {len(nums)} | ids mapped: {len(aux)} | blocks: {len(blocks)} -> {out}")
    return out


def check(project):
    """Log, KaTeX render errors, dangling anchors, PDF margins and links.  Needs headless Chrome and PyMuPDF."""
    cfg, out = load_project(project)
    problems = 0
    log = (out / ".tex/.temp/main.log").read_text(errors="ignore")
    bad = [l for l in log.splitlines() if re.search(r"Undefined|Multiply|undefined|Overfull \\hbox \((\d{2,})|Token not allowed", l)]
    print("log problems:", bad[:6] or "none"); problems += len(bad)
    chrome = os.environ.get("CHROME") or next((c for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome") or "", shutil.which("chromium") or "") if c and os.path.exists(c)), None)
    if chrome:
        dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--virtual-time-budget=30000", "--dump-dom", "file://" + str(out / f"{PREFIX}.html")], capture_output=True, text=True).stdout
        ids = set(re.findall(r'id="([^"]+)"', dom)); hs = set(re.findall(r'href="#([^"]+)"', dom))
        err = len(re.findall(r'class="katex-error"', dom)); dang = sorted(h for h in hs if h not in ids)
        print("katex errors:", err, "| dangling anchors:", dang[:6]); problems += err + len(dang)
    else:
        print("no Chrome found: KaTeX render check skipped (set CHROME)")
    try:
        import pymupdf
        d = pymupdf.open(out / f"{PREFIX}.pdf")
        over = sum(1 for p in d for b in p.get_text("dict")["blocks"] for ln in b.get("lines", []) for sp in ln["spans"] if sp["bbox"][2] > p.rect.width - 40)
        print("pages:", len(d), "| spans past right margin:", over, "| outline entries:", len(d.get_toc())); problems += over
    except ImportError:
        print("PyMuPDF not installed: PDF margin check skipped")
    return problems


def refs_report(project, block):
    load_project(project)
    blk = parse(BLOCKS_DIR / f"{block}.txt")
    lines = {it["id"]: it for st in blk["steps"] for it in st["items"] if it["kind"] == "line"}
    for st in blk["steps"]:
        for it in st["items"]:
            t = it["lead"] if it["kind"] == "line" else it["text"]
            cites = ID_LINE.findall("".join(seg for i, seg in enumerate(t.split("$")) if i % 2 == 0))
            if cites:
                print(f"{it.get('id', '(prose)')}:")
                for c in cites:
                    print(f"    {c} = {lines[c]['tex'][:70]}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Proof-centred reading page and PDF from block sources.")
    ap.add_argument("command", choices=["build", "check", "refs"])
    ap.add_argument("project", help="project directory holding book.json, blocks/*.txt, context.json")
    ap.add_argument("--block", help="block id for 'refs'")
    ap.add_argument("--builder", help="LaTeX command template with {tex}; default latexmk -lualatex")
    a = ap.parse_args(argv)
    if a.command == "build":
        build(a.project, a.builder)
    elif a.command == "check":
        sys.exit(1 if check(a.project) else 0)
    else:
        refs_report(a.project, a.block)


if __name__ == "__main__":
    main()
