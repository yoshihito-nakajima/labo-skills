#!/usr/bin/env python3
"""Build the section-structured page and the matching TeX parts from one section record.

Usage:
  build_section_page.py RECORD.json --out DIR [--base BASE] [--original PDF]

Writes DIR/index.html (collapsed hierarchy, single file), DIR/panels/p<ID>.tex (section head
panels), DIR/codecards/c<ID>.tex (Steps and comparison cards) and DIR/overview.tex. Code
paths in the record are relative to BASE (default: the record's directory). With --original,
sections that give `heading_word` get the original page region (heading to next heading) as an
embedded image beside the translation file `translation_html` (optional, a path to an HTML
fragment). See references/companion/section-page.md and reading-reference/references/survey-profile.md.
Needs only the standard library; pandoc (math to MathML), pdftotext and pdftoppm are used when present.
"""
import argparse, base64, html, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import code_langs as CL
USED = set()  # language keys met while writing TeX listings

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

    def root(self, i):
        a = self.anc(i); return a[-1] if a else i

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

def _overlap(x, f, a, b):
    return bool(x) and not isinstance(x, dict) and x[0] == f and not (x[2] < a or x[1] > b)


def compare_notes(R, cm, f, a, b):
    """Notes for the comparison rows whose lines overlap f:a-b: the status and the counterpart lines on the other side."""
    out = []
    for r in (cm or {}).get("rows", []):
        for mine, other, oname in ((r.get("left"), r.get("right"), cm["right"]["name"]), (r.get("right"), r.get("left"), cm["left"]["name"])):
            if not _overlap(mine, f, a, b): continue
            lab, cls = STATUS[r["status"]]
            if not other: where = f"{m(oname)} has no corresponding lines"
            elif isinstance(other, dict): where = f"in {m(oname)}: one line <code>{esc(other['lit'])}</code>"
            else: where = f"{m(oname)}, <code>{esc(other[0])}</code> lines {other[1]}-{other[2]}"
            out.append(f'<div class="cnote {cls}"><span class="stl {cls}">{lab}</span> <b>{esc(r["label"])}</b>. Counterpart: {where}. {m(r["why"])}</div>')
            break
    return "".join(out)


def api_card(x):
    return (f'<div class="apic"><b><code>{esc(x["name"])}</code></b> <code class="small">{esc(x.get("sig", ""))}</code><br><b>returns:</b> {m(x.get("ret", ""))}<br><b>note:</b> {m(x.get("note", ""))}'
            + (f'<br><b>cost:</b> {m(x["cost"])}' if x.get("cost") else "") + (f'<div class="small muted">{esc(x["quote"])}</div>' if x.get("quote") else "") + '</div>')


def api_calls(x, text):
    """True when the (comment-stripped) lines call the function: name followed by '(' and not part of a longer dotted name."""
    return re.search(r"(?<![\w.])" + re.escape(x["name"]) + r"\s*\(", text) is not None


def api_inline(R, st, a, b, seen):
    """Specs of the functions called on lines a-b, matched automatically by name; the full card at the first line of the code section that calls it, a short pointer after."""
    if not st.get("apis"): return ""
    L = R.lines(st["file"], a, b)
    txt = "\n".join(re.split(r"#|%|//", l)[0] for l in L)
    out = []
    for x in st["apis"]:
        if not api_calls(x, txt): continue
        if x["name"] in seen: out.append(f'<div class="apic small muted"><code>{esc(x["name"])}</code>: same as above (first call).</div>')
        else: seen.add(x["name"]); out.append(api_card(x))
    return "".join(out)


def unplaced_apis(R, st):
    """Specs whose function name is called on none of the Step's lines (the checker reports these)."""
    txt = "\n".join(re.split(r"#|%|//", l)[0] for l in R.lines(st["file"], st["first"], st["last"]))
    return [x["name"] for x in st.get("apis", []) if not api_calls(x, txt)]


def annotated_code(R, st, cm, seen=None):
    """Each note stands directly above the lines it explains; the comparison counterpart and the specs of the functions called on those lines follow the note."""
    f = st["file"]; L = R.lines(f, st["first"], st["last"]); out = []; seen = set() if seen is None else seen
    for a, b, text in st["lines"]:
        body = "\n".join(f'<span class="ln">{n}</span> {esc(L[n - st["first"]])}' for n in range(a, b + 1))
        rng = f"line {a}" if a == b else f"lines {a}-{b}"
        out.append(f'<div class="ablk"><div class="anote"><span class="alab">{rng}</span> {m(text)}</div>{compare_notes(R, cm, f, a, b)}{api_inline(R, st, a, b, seen)}<pre class="cb">{body}</pre></div>')
    return f'<div class="acode">{"".join(out)}</div><div class="muted small">{esc(f)} {st["first"]}-{st["last"]} (notes are display only; the file is unchanged)</div>'


def plain_code(R, s):
    """The whole code with nothing added: one heading per Step, then the verbatim lines. Shown open, before the annotated version."""
    out = []
    for st in s["steps"]:
        body = "\n".join(f'<span class="ln">{st["first"] + i}</span> {esc(l)}' for i, l in enumerate(R.lines(st["file"], st["first"], st["last"])))
        out.append(f'<div class="step plain"><h4>{esc(st["title"])}</h4><pre class="cb">{body}</pre><div class="muted small">{esc(st["file"])} {st["first"]}-{st["last"]}</div></div>')
    return "".join(out)


def annotated_body(R, s):
    seen = set(); out = []
    for st in s["steps"]:
        for nm in unplaced_apis(R, st): print(f'warning: {s["id"]}: step {st["title"]!r}: the spec of {nm!r} matches no call on the Step\'s lines, so it is not shown', file=sys.stderr)
        out.append(f'<div class="step"><h4>{m(st["title"])}</h4><p>{m(st["what"])}</p>{annotated_code(R, st, s.get("comparison"), seen)}<p class="mapto"><b>Math:</b> {m(st["math"])}</p></div>')
    return "".join(out)


def card_html(R, s):
    out = [f'<p>Steps below show verbatim lines; the math correspondence follows each code block.</p>']
    if s.get("flow"): out.append(f'<details class="flow goal" open><summary><b>Goal of this code as a whole, and why this tool</b></summary><p>{m(s["flow"])}</p>' + (f'<p>{m(s["why"])}</p>' if s.get("why") else "") + '</details>')
    out.append(f'<details class="plaincode" open><summary><b>The code as a whole, with nothing added</b></summary>{plain_code(R, s)}</details>')
    out.append('<details class="annotated"><summary><b>The same code with a note above every line (comparison counterpart and called-function specs on the line)</b></summary>')
    out.append(annotated_body(R, s))
    out.append('</details>')
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


def stitch(parts):
    """Join per-page crops [(page, jpeg bytes)] into one tall image: the section's region in one place.
    A thin dotted line and a small page label mark each page break. Needs Pillow."""
    from PIL import Image, ImageDraw, ImageFont
    import io
    ims = [(p, Image.open(io.BytesIO(b)).convert("RGB")) for p, b in parts]
    w = max(im.width for _, im in ims); canvas = Image.new("RGB", (w, sum(im.height for _, im in ims)), "white"); y = 0; dr = ImageDraw.Draw(canvas)
    try: font = ImageFont.load_default(size=14)
    except TypeError: font = ImageFont.load_default()
    for n, (p, im) in enumerate(ims):
        canvas.paste(im, (0, y))
        if n:
            for x in range(0, w, 12): dr.line([(x, y), (x + 6, y)], fill=(120, 140, 160))
            dr.rectangle([w - 58, y, w, y + 18], fill=(235, 241, 247)); dr.text((w - 54, y + 1), f"p.{p}", fill=(60, 80, 100), font=font)
        y += im.height
    buf = io.BytesIO(); canvas.save(buf, "JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def crops(R, s, pdf, words):
    """Returns ([(first_page, data_uri, pages)], description): one stitched image for the whole region."""
    order = [x["id"] for x in R.S]; k = order.index(s["id"])
    st = locate(words, s["id"], s.get("heading_word", ""), *s["pages"])
    nxt = R.BY[order[k + 1]] if k + 1 < len(order) else None
    nx = locate(words, nxt["id"], nxt.get("heading_word", ""), *nxt["pages"]) if nxt else None
    if not st: return [], "heading not located; showing whole pages"
    en = nx or (st[0], 800); parts = []; sc = 110 / 72
    for p in range(st[0], en[0] + 1):
        y0 = st[1] - 6 if p == st[0] else 70; y1 = en[1] - 6 if p == en[0] else 706
        if y1 - y0 < 14: continue
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["pdftoppm", "-r", "110", "-f", str(p), "-l", str(p), "-x", "60", "-y", str(int(y0 * sc)), "-W", str(int(480 * sc)), "-H", str(int((y1 - y0) * sc)), "-jpeg", str(pdf), d + "/x"], check=True, capture_output=True)
            parts.append((p, open(d + "/" + sorted(os.listdir(d))[0], "rb").read()))
    if not parts: return [], "empty region"
    try: uri = stitch(parts)
    except ImportError: return [(p, "data:image/jpeg;base64," + base64.b64encode(b).decode(), [p]) for p, b in parts], "Pillow missing: pages shown separately"
    return [(parts[0][0], uri, [p for p, _ in parts])], f"from the heading of §{s['id']} on p.{st[0]} to the next heading, as one continuous region"


def orig_html(R, s, pdf, words, same=None):
    tr = ""
    if s.get("translation_html"): tr = (R.base / s["translation_html"]).read_text(encoding="utf-8")
    elif s.get("translation"): tr = "".join(f"<p>{m(p)}</p>" for p in s["translation"])
    imgs, desc = ([], "")
    if pdf and s.get("heading_word"): imgs, desc = crops(R, s, pdf, words)
    left = "".join(f'<div class="origscroll"><figure><img {("data-same=" + chr(34) + same + chr(34)) if same else ("src=" + chr(34) + u + chr(34))} alt="p.{pl[0]}"><figcaption>p.{pl[0]}' + (f'-{pl[-1]}' if len(pl) > 1 else '') + ' (original, this section only; page breaks marked by dotted lines)</figcaption></figure></div>' for p, u, pl in imgs) + ('<button class="small" onclick="this.previousElementSibling.classList.toggle(\'full\')">expand / collapse the original column</button>' if imgs else '') or '<p class="muted">no original region (give --original and heading_word)</p>'
    return f'<div class="otgrid"><div><h4>Original</h4><p class="small muted">{esc(desc)}</p>{left}</div><div><h4>Faithful translation</h4>{tr or "<p class=muted>(none)</p>"}</div></div>'


CSS = """body{font-family:system-ui,sans-serif;max-width:1200px;margin:0 auto;padding:0 1rem;line-height:1.5}details.blk{border:1px solid #cdd;border-radius:6px;margin:.5rem 0}details.blk>summary{cursor:pointer;padding:.4rem .7rem;font-weight:600;background:#f3f6f8}.inner{padding:.5rem .8rem}
.panel2 table{width:100%;border-collapse:collapse}.panel2 th{width:8rem;text-align:left;vertical-align:top;font-size:.85rem;color:#055}.by{font-size:.72rem;padding:0 .35rem;border-radius:3px;margin-right:.2rem;background:#eee}.by-author,.by-official{background:#d8f0dc}.by-lib{background:#e3eaf8}.by-ai{background:#fbe3d0}
.figcard{border:1px solid #cdd;border-radius:6px;margin:.8rem 0;padding:.4rem .8rem}.fromprev{background:#fff8e6;border-left:4px solid #e0a030;padding:.25rem .6rem;margin:.3rem 0}.say{background:#fff8e6;border-left:4px solid #e0a030;padding:.3rem .7rem;margin:.4rem 0}.rd{margin:1.2rem 0;border-top:1px solid #dde}.cb{background:#fbfbfd;border:1px solid #dde;padding:.3rem .5rem;font-size:.78rem;overflow:auto;white-space:pre}.cb .ln{color:#999;margin-right:.5rem}.cb.same{background:#eef8ee}.cb.chg{background:#fff8dc}.cb.onl{background:#eaf1fb}.cb.none{color:#999}.step{border-left:3px solid #9bc;padding:0 .6rem;margin:.6rem 0}.cmprow{margin:.5rem 0;padding:.3rem .5rem;border-radius:4px}
.cmprow.same{background:#f2faf2}.cmprow.chg{background:#fffbe9}.cmprow.onl{background:#f1f6fc}.cmpgrid,.otgrid{display:grid;grid-template-columns:1fr 1fr;gap:.6rem}.otgrid img{max-width:100%;border:1px solid #ccd}.stl{font-size:.75rem;padding:0 .4rem;border-radius:3px;font-weight:700}.stl.same{background:#bfe3c1}.stl.chg{background:#f3dd7c}.stl.onl{background:#b9d0ee}.muted{color:#777}.small{font-size:.85rem}
.ledcard{border:1px solid #cdd;border-radius:6px;margin:.35rem 0;background:#fff}.ledcard>summary{cursor:pointer;padding:.35rem .6rem;background:#f6f9fa}.ledcard>.inner{padding:.4rem .8rem}.sumgist{font-weight:400;font-size:.88rem;color:#345}.ledctl{margin:.4rem 0}.origscroll{max-height:85vh;overflow-y:auto;border:1px solid #ccd}.origscroll.full{max-height:none}.gist{background:#eef7f3;border-left:3px solid #4a9;padding:.25rem .5rem}.gistlist{background:#f6faf8;border:1px solid #cde;border-radius:6px;padding:.3rem .7rem;margin:.4rem 0}.lead,.bridge,.flow{background:#f7fbf9;border-left:4px solid #6b9;padding:.4rem .8rem;margin:.5rem 0}.bridge,.flow.after{border-left-color:#c96;background:#fcf9f5}.apic{border:1px solid #dde;padding:.3rem .5rem;margin:.3rem 0;font-size:.88rem}.acode{margin:.3rem 0}.ablk{margin:.1rem 0 .5rem}.anote{background:#f3f7fb;border-left:3px solid #6a9fd0;padding:.25rem .6rem;line-height:1.7}.alab{font-size:.75rem;color:#356;font-weight:700;margin-right:.3rem}.cnote{padding:.2rem .6rem;font-size:.88rem;border-left:3px solid #aaa}.cnote.same{background:#eef8ee}.cnote.chg{background:#fff8dc}.cnote.onl{background:#eaf1fb}.ablk .cb{margin:0}.figin{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.figin img{max-width:100%}@media(max-width:900px){.cmpgrid,.otgrid,.figin{grid-template-columns:1fr}}"""


def ledger_parts(R, s):
    """Concepts and claims of a section from the record (optional). A reference to a concept never shows an id alone:
    the name and the one-line gist travel with it, so the reader need not open the ledger."""
    cb = {c["id"]: c for c in R.d.get("concepts", [])}
    cs = [cb[c] for c in s.get("concepts", []) if c in cb]
    return cb, cs, s.get("claims", [])


def _used(R):
    u = {}
    for sec in R.S:
        for x in sec.get("claims", []):
            for r in x.get("concepts", []): u.setdefault(r, []).append((x, sec))
    return u


def _home(R):
    return {r: sec for sec in R.S for r in sec.get("concepts", [])}


def _cdetails(c, sec_id, body, scope):
    """One folded concept: id prefix 'sc-' in the section ledger, 'a-' in the appendix. The folded line carries the gist."""
    pre = "sc" if scope == "sec" else "a"
    return (f'<details class="ledcard" id="{pre}-{esc(c["id"])}"><summary><b>{esc(c["id"])}</b> {m(c["name"])}'
            f'<div class="sumgist">{m(c["gist"])}</div></summary><div class="inner">{body}</div></details>')


def _cbody(R, c, scope):
    used = _used(R).get(c["id"], []); home = _home(R).get(c["id"])
    us = ", ".join(f'<a href="#ss-{esc(x["id"])}">{esc(x["id"])}</a> (\u00a7{esc(sec["id"])})' for x, sec in used) or "(none)"
    back = (f'<a href="#a-{esc(c["id"])}">see in the appendix ledger</a>' if scope == "sec"
            else (f'<a href="#sc-{esc(c["id"])}">see in the ledger of \u00a7{esc(home["id"])}</a>' if home else ""))
    return (f'<p class="gist"><b>In short:</b> {m(c["gist"])}</p><p><b>Explanation:</b> {m(c["explain"])}</p>'
            f'<p><b>Precise definition:</b> {m(c.get("definition", ""))}</p><p class="small"><b>Claims that use it:</b> {us}</p>'
            + (f'<p class="small">\u2197 {back}</p>' if back else ""))


def _sdetails(R, x, sec, scope):
    cb = {c["id"]: c for c in R.d.get("concepts", [])}; home = _home(R)
    pre = "ss" if scope == "sec" else "as"
    # a reference goes to the ledger of the same scope: the concept's home section, or the appendix entry
    def tgt(r): return f"#sc-{esc(r)}" if scope == "sec" else f"#a-{esc(r)}"
    refs = "".join(f'<li><a href="{tgt(r)}">{esc(r)}</a> <b>{m(cb[r]["name"])}</b> \u2014 {m(cb[r]["gist"])}</li>' for r in x.get("concepts", []) if r in cb)
    back = f'<a href="#as-{esc(x["id"])}">see in the appendix ledger</a>' if scope == "sec" else f'<a href="#ss-{esc(x["id"])}">see in the ledger of \u00a7{esc(sec["id"])}</a>'
    return (f'<details class="ledcard" id="{pre}-{esc(x["id"])}"><summary><b>{esc(x["id"])}</b> <span class="muted small">\u00a7{esc(sec["id"])} status {esc(x.get("status", "?"))}</span>'
            f'<div class="sumgist">{m(x["text"])}</div></summary><div class="inner"><p><b>Claim:</b> {m(x["text"])}</p>'
            + (f'<p><b>Proof or locator:</b> {m(x["proof"])}</p>' if x.get("proof") else "")
            + (f'<div class="small"><b>Concepts used:</b><ul>{refs}</ul></div>' if refs else "") + f'<p class="small">\u2197 {back}</p></div></details>')


LEDCTL = '<div class="ledctl small"><button onclick="ledAll(this,true)">open all</button> <button onclick="ledAll(this,false)">close all</button></div>'


def ledger_auto_html(R, s):
    cb, cs, ss = ledger_parts(R, s)
    if not (cs or ss): return ""
    h = [LEDCTL]
    if cs: h.append('<div class="gistlist"><b>Concepts of this section, one line each:</b><ul>' + "".join(f'<li><a href="#sc-{esc(c["id"])}">{esc(c["id"])}</a> <b>{m(c["name"])}</b> \u2014 {m(c["gist"])}</li>' for c in cs) + '</ul></div>')
    for c in cs: h.append(_cdetails(c, s["id"], _cbody(R, c, "sec"), "sec"))
    for x in ss: h.append(_sdetails(R, x, s, "sec"))
    return "".join(h)


def appendix_ledger_html(R):
    """The overall ledger: folded as a whole and per entry, linked both ways with the section ledgers."""
    cs = R.d.get("concepts", [])
    if not cs: return ""
    claims = [(x, sec) for sec in R.S for x in sec.get("claims", [])]
    h = [f'<details class="blk"><summary><b>Concepts</b> ({len(cs)})</summary><div class="inner">{LEDCTL}' + "".join(_cdetails(c, None, _cbody(R, c, "app"), "app") for c in cs) + '</div></details>']
    h.append(f'<details class="blk"><summary><b>Claims</b> ({len(claims)})</summary><div class="inner">{LEDCTL}' + "".join(_sdetails(R, x, sec, "app") for x, sec in claims) + '</div></details>')
    return "".join(h)


def ledger_auto_tex(R, s):
    cb, cs, ss = ledger_parts(R, s)
    if not (cs or ss): return ""
    t = []
    if cs:
        t.append(r"{\small\textbf{Concepts of this section, one line each}}\begin{itemize}\small")
        t += [f"\\item {tx(c['name'])} --- {tx(c['gist'])}" for c in cs]; t.append(r"\end{itemize}")
    for c in cs:
        t.append(f"\\paragraph{{{c['id']}\\ {tx(c['name'])}}}\\begin{{itemize}}\\small\\item In short: {tx(c['gist'])}\\item Explanation: {tx(c['explain'])}\\item Definition: {tx(c.get('definition', ''))}\\end{{itemize}}")
    for x in ss:
        refs = "; ".join(f"{r} {tx(cb[r]['name'])} ({tx(cb[r]['gist'])})" for r in x.get("concepts", []) if r in cb)
        t.append(f"\\paragraph{{{x['id']}}}\\begin{{itemize}}\\small\\item Claim: {tx(x['text'])}" + (f"\\item Proof or locator: {tx(x['proof'])}" if x.get("proof") else "") + (f"\\item Concepts used: {refs}" if refs else "") + "\\end{itemize}")
    return "\n".join(t) + "\n"


def section_html(R, s, pdf, words):
    i = s["id"]; parts = [f'<div class="say"><b>What this section says</b>: {m(s["question"])} → {m(s["answer"])}</div>',
                          f'<details class="blk" id="p-{i}" open><summary>Section structure</summary><div class="inner">{panel_html(R, s)}</div></details>']
    parts.append(f'<details class="blk" id="ot-{i}"><summary>Original and faithful translation ({pages(s)})</summary><div class="inner">{orig_html(R, s, pdf, words)}</div></details>')
    if s.get("figures"):
        fig = ""
        for f in s["figures"]:
            d = R.FIGS[f]; img = f'<img src="{esc(d["image"])}" alt="{esc(f)}">' if d.get("image") else ""
            rel = "".join(f'<li>{esc(a)} → {esc(b)}: <b>{esc(k)}</b>. {m(dd)}</li>' for a, b, k, dd in R.d.get("figure_links", []) if f in (a, b))
            fig += f'<div class="figin"><div>{img}</div><div><h4>{esc(f)} (p.{d["page"]})</h4><p>{m(d["what"])}</p><p>{m(d.get("text", ""))}</p><p><b>Colour:</b> {m(d["color"])}</p>{"<ul>" + rel + "</ul>" if rel else ""}</div></div>'
        parts.append(f'<details class="blk" id="figs-{i}"><summary>Figures of this section</summary><div class="inner">{fig}</div></details>')
    if s.get("steps"): parts.append(f'<details class="blk" id="cu-{i}"><summary>Code: whole code, annotated version, comparison</summary><div class="inner">{card_html(R, s)}</div></details>')
    if s.get("glossary"):
        gl = "".join(f'<tr><td><b>{m(w)}</b></td><td>{m(d)}</td><td class="small">{esc(wh)}</td><td class="small">{esc(fl)}</td></tr>' for w, d, wh, fl in s["glossary"])
        parts.append(f'<details class="blk" id="gl-{i}"><summary>Terms in this section ({len(s["glossary"])})</summary><div class="inner"><table><tr><th>term</th><th>plain explanation and what it is good for</th><th>where</th><th>field</th></tr>{gl}</table></div></details>')
    if not s.get("ledger_html"): s = dict(s, ledger_html=ledger_auto_html(R, s))
    if s.get("ledger_html"): parts.append(f'<details class="blk" id="led-{i}"><summary>Math ledger of this section</summary><div class="inner">{s["ledger_html"]}</div></details>')
    if s.get("explanation_html"): parts.append(f'<details class="blk" id="ex-{i}"><summary>Explanation</summary><div class="inner">{(R.base / s["explanation_html"]).read_text(encoding="utf-8")}</div></details>')
    kids = "".join(section_html(R, k, pdf, words) for k in R.kids(i))
    bridge = f'<div class="bridge"><b>To the next section</b><p>{m(s["bridge"])}</p></div>' if s.get("bridge") else ""
    w = " ".join(f"{n}{v}" for n, v in zip(("math", "code", "fig"), s.get("weights", [0, 0, 0])))
    kinds = " ".join(badge(c["kind"]) for c in s.get("code", []) if c.get("kind") != "none")
    return (f'<details class="blk" id="sec-{i}"><summary>§{i} {esc(s["title"])} <span class="muted small">{pages(s)} {w}</span> {kinds}'
            f'<div class="small" style="font-weight:400">{m(s.get("sell", ""))}</div></summary><div class="inner">{"".join(parts)}{kids}{bridge}</div></details>')


def reading_html(R, pdf=None, words=None):
    """First read, no preconceptions: per section the original (left) and the faithful translation (right), then what the section says; the whole picture comes last."""
    chapters = []  # [(top section, [parts])]: one fold per top-level section; subsections stay inside it, unfolded
    for s in R.S:
        i = s["id"]; lv = i.count("."); h = 3 + min(lv, 2)
        if not s.get("parent") or not chapters: chapters.append((s, []))
        out = chapters[-1][1]
        has_text = bool(s.get("translation_html") or s.get("translation"))
        head = f'<h{h}>§{i} {esc(s["title"])} <span class="muted small">{pages(s)}</span></h{h}>'
        if not has_text:
            out.append(f'<div class="rd lv{lv}" id="rd-{i}">{head}<p class="muted small">(This section is only a heading; its text starts in the subsections below.)</p></div>')
            continue
        jump = [f'<a href="#sec-{i}">deep dive</a>']
        if s.get("figures"): jump.append("figures: " + ", ".join(f'<a href="#figs-{i}">{esc(f)}</a>' for f in s["figures"]))
        if s.get("steps"): jump.append(f'<a href="#cu-{i}">code</a>')
        out.append(f'<div class="rd lv{lv}" id="rd-{i}">{head}{orig_html(R, s, pdf, words or {}, same=f"ot-{i}")}'
                   f'<div class="say"><b>What this section says</b>: {m(s["question"])} → {m(s["answer"])}</div><p class="small">{" / ".join(jump)}</p></div>')
    tops = [s for s in R.S if not s.get("parent")]
    def chb(s):  # the bridge that leaves a chapter is the bridge of its last descendant
        while R.kids(s["id"]): s = R.kids(s["id"])[-1]
        return s.get("bridge")
    pic = ('<div class="rd" id="whole"><h3>The whole picture (read after all sections)</h3>'
           + (f'<p>{m(R.d["whole_picture"])}</p>' if R.d.get("whole_picture") else "")
           + "<ol>" + "".join(f'<li>§{s["id"]} <b>{esc(s["title"])}</b>: {m(s["question"])} → {m(s["answer"])}' + (f'<br><span class="small">→ next chapter: {m(chb(s))}</span>' if chb(s) else "") + '</li>' for s in tops) + '</ol></div>')
    folds = "".join(f'<details class="blk rdch" id="rdc-{t["id"]}"{" open" if n == 0 else ""}><summary>§{t["id"]} {esc(t["title"])} <span class="muted small">{pages(t)}</span></summary><div class="inner">{"".join(parts)}</div></details>' for n, (t, parts) in enumerate(chapters))
    return folds + pic


def _chapter_folds(R, items, label):
    """items: [(home section id, html card, name)] -> one fold per chapter (top-level section) in section order, the first open; the heading lists the names."""
    order = {s["id"]: n for n, s in enumerate(R.S)}
    by = {}
    for sid, card, name in items: by.setdefault(R.root(sid), []).append((card, name))
    out = []
    for n, root in enumerate(sorted(by, key=lambda r: order[r])):
        t = R.BY[root]
        out.append(f'<details class="blk" id="{label}-{root}"{" open" if n == 0 else ""}><summary>§{root} {esc(t["title"])} <span class="muted small">{pages(t)}</span> — {esc(", ".join(dict.fromkeys(x for _, nm in by[root] for x in nm.split(", "))))}</summary><div class="inner">{"".join(c for c, _ in by[root])}</div></details>')
    return "".join(out)


def fig_flow_html(R):
    """Same build as Reading: sections in paper order, folded per chapter (first fold open), and under each section ALL of its figures
    (a figure used in several sections appears, with the same content, under each). Sections without figures are skipped.
    Card: what it follows from, the original figure, what to look at and how to read it, colours, terms (with basis), the other sections where it occurs."""
    rel = R.d.get("figure_links", []); items = []
    def card(sid, f):
        d = R.FIGS[f]
        prev = "".join(f'<div class="fromprev"><b>From {m(a)}</b>: {esc(k)}. {m(dd)}</div>' for a, b, k, dd in rel if b == f)
        img = f'<img src="{esc(d["image"])}" alt="{esc(f)}">' if d.get("image") else ""
        terms = d.get("terms") or []
        tt = ('<table><tr><th>term</th><th>what it is and what it is good for</th><th>basis</th></tr>' + "".join(f'<tr><td><b>{m(w)}</b></td><td>{m(ds)}</td><td class="small">{esc(bs)}</td></tr>' for w, ds, bs in terms) + '</table>') if terms else '<p class="muted small">(no terms recorded)</p>'
        others = [s["id"] for s in R.S if f in s.get("figures", []) and s["id"] != sid]
        where = ("Also in: " + ", ".join(f'<a href="#sec-{o}">§{o}</a>' for o in others) + ".") if others else "This figure occurs only in this section."
        return (f'<div class="figcard" id="ff-{sid}-{esc(f)}"><h4>{esc(f)} (p.{d["page"]})</h4>{prev}'
                f'<div class="figin"><div>{img}</div><div><p>{m(d["what"])}</p><p>{m(d.get("text", ""))}</p><p><b>Colour:</b> {m(d["color"])}</p></div></div>'
                f'<div class="figterms"><b>Terms for reading this figure</b>{tt}</div><p class="small">{where}</p></div>')
    for s in R.S:
        if not s.get("figures"): continue
        i = s["id"]; h = 3 + min(i.count("."), 2)
        head = f'<h{h}>§{i} {esc(s["title"])} <span class="muted small">{pages(s)}</span></h{h}><p class="small"><a href="#rd-{i}">Reading</a> / <a href="#sec-{i}">deep dive</a></p>'
        items.append((i, f'<div class="rd" id="ffs-{i}">{head}' + "".join(card(i, f) for f in s["figures"]) + '</div>', ", ".join(s["figures"])))
    note = '<p class="small muted">Built like Reading: sections in paper order, folded per chapter (first fold open), each section carrying all of its figures; a figure used in several sections is shown in each, with the same content. A term whose basis is not the paper itself is marked as such and unchecked.</p>'
    return note + _chapter_folds(R, items, "ffc")


def code_flow_html(R):
    """Sections in paper order, folded per chapter, each with the code of the section in two blocks: what it follows from, kind/state, goal and why, the whole code with nothing added (open), the annotated code (folded; comparison, function specs and math on the lines/Steps), terms, where it occurs."""
    cs = [s for s in R.S if s.get("steps")]
    if not cs: return '<p class="muted">(no code)</p>'
    ids = {s["id"] for s in cs}; items = []
    for s in cs:
        i = s["id"]
        prev = "; ".join(f'<a href="#cf-{o}">§{o}</a>: {m(w)}' for o, w in R.edges_of(i, "recv") if o in ids)
        fromprev = f'<div class="fromprev"><b>From the code of</b> {prev}</div>' if prev else '<div class="muted small">(no direct link from another code section)</div>'
        kinds = " ".join(badge(c["kind"]) + f' {esc(c["name"])} <span class="muted small">[{esc(c.get("state", ""))}{", " + esc(c["lic"]) if c.get("lic") else ""}]</span>' for c in s.get("code", []) if c.get("kind") != "none")
        cm = s.get("comparison")
        legend = (f'<p class="small"><span class="stl same">same</span> <span class="stl chg">changed</span> <span class="stl onl">only on one side</span> {esc(cm["title"])}. {esc(summary(cm))}</p>') if cm else '<p class="small muted">(no comparison)</p>'
        gl = s.get("glossary") or []
        gt = ('<table><tr><th>term</th><th>what it is and what it is good for</th></tr>' + "".join(f'<tr><td><b>{m(w)}</b></td><td>{m(d)}</td></tr>' for w, d, _, _ in gl) + '</table>') if gl else ""
        card = (f'<div class="figcard" id="cf-{i}"><h4>§{i} {esc(s["title"])}</h4>{fromprev}<p>{kinds}</p>'
                f'<div class="flow goal"><b>Goal, and why this tool</b><p>{m(s.get("flow", ""))}</p><p>{m(s.get("why", ""))}</p></div>'
                f'<details class="plaincode" open><summary><b>1. The code as a whole, with nothing added (a heading per Step only)</b></summary>{plain_code(R, s)}</details>'
                f'<details class="annotated"><summary><b>2. The same code with a note above every line (comparison counterpart, called-function specs and math correspondence included)</b></summary>{legend}{annotated_body(R, s)}</details>'
                + (f'<div class="figterms"><b>Terms of this section</b>{gt}</div>' if gt else "")
                + f'<p class="small">Occurs in: <a href="#cu-{i}">§{i}, code in the deep dive (the same two blocks plus the comparison table)</a>.</p></div>')
        items.append((i, card, f"§{i}"))
    return '<p class="small muted">Code sections in paper order, folded per chapter (first fold open). Each section carries its code twice: the whole code with nothing added, and the same code with a note above every line (function specs sit on the line that calls them).</p>' + _chapter_folds(R, items, "cfc")


def build_html(R, pdf=None):
    words = read_words(pdf) if pdf else {}
    secs = "".join(section_html(R, s, pdf, words) for s in R.S if not s.get("parent"))
    ov = "<ol>" + "".join(f'<li>§{s["id"]} <b>{esc(s["title"])}</b>: {m(s["question"])} → {m(s["answer"])}</li>' for s in R.S if not s.get("parent")) + "</ol>"
    frows = "".join(f'<tr id="fig-{esc(f)}"><td>{esc(f)}</td><td>p.{d["page"]}</td><td>{m(d["what"])}</td><td>{m(d["color"])}</td></tr>' for f, d in R.FIGS.items())
    crow = "".join(f'<tr><td><a href="#sec-{s["id"]}">§{s["id"]}</a></td><td>{esc(c["name"])}</td><td>{badge(c["kind"])}</td><td>{esc(c.get("src", ""))}</td><td>{esc(c.get("state", ""))}</td><td>{esc(c.get("lic", ""))}</td></tr>' for s in R.S for c in s.get("code", []) if c.get("kind") != "none")
    def top(i, t, b, op=False): return f'<details class="blk" id="{i}"{" open" if op else ""}><summary>{t}</summary><div class="inner">{b}</div></details>'
    body = (top("reading", "1 Reading (original and faithful translation, section by section; the whole picture at the end)", reading_html(R, pdf, words), True)
            + top("figflow", "2 Figure flow (same order as Reading: per section, all of its figures; link from the previous figure, original, how to read it, colours, terms)", fig_flow_html(R))
            + top("codeflow", "3 Code flow (sections with code, in paper order)", code_flow_html(R))
            + top("secs", "4 Deep dive (per section: what it says, original and translation, figures, code, terms, ledger)", secs)
            + top("appx", "5 Appendix (indexes and materials)",
                  top("figs", "Figure list", f"<table><tr><th>figure</th><th>page</th><th>content</th><th>colour legend</th></tr>{frows}</table>")
                  + top("codes", "Code list", f"<table><tr><th>section</th><th>code</th><th>kind</th><th>source</th><th>state</th><th>licence</th></tr>{crow}</table>")
                  + top("ledger", "Ledger (concepts, claims)", R.d.get("ledger_html") or appendix_ledger_html(R) or "<p class=muted>(attach the ledger here)</p>")
                  + R.d.get("appendix_html", "<p class=muted>materials, acquisition state, request list</p>")))
    js = ("<script>function ledAll(b,o){b.parentElement.parentElement.querySelectorAll('details.ledcard').forEach(function(d){d.open=o})}"
          "function openTo(h){var e=document.getElementById(h);while(e){if(e.tagName==='DETAILS')e.open=true;e=e.parentElement}}"
          "addEventListener('hashchange',function(){var h=location.hash.slice(1);if(h){openTo(h);var t=document.getElementById(h);if(t)t.scrollIntoView()}});"
          "if(location.hash)openTo(location.hash.slice(1));document.querySelectorAll('img[data-same]').forEach(function(im){var e=document.getElementById(im.dataset.same);var s=e&&e.querySelector('img');if(s&&s.src)im.src=s.src});</script>")
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(R.d.get("title", ""))}</title><style>{CSS}</style></head><body><h1>{esc(R.d.get("title", ""))}</h1><p class="small muted">{esc(R.d.get("source", ""))}. Private page; do not publish.</p>{body}{js}</body></html>'


# --- TeX ---
def lst(R, x, tag, litdir):
    if not x: return r"\par{\small\itshape (not on this side)}"
    if isinstance(x, dict):
        litdir.mkdir(parents=True, exist_ok=True); (litdir / f"{tag}.txt").write_text(x["lit"] + "\n"); return r"\lstinputlisting[numbers=none]{%s}" % (litdir / f"{tag}.txt")
    f, a, b = x; sp = CL.spec(f); USED.add(sp.get("key"))
    return r"\lstinputlisting[%sfirstline=%d,lastline=%d,firstnumber=%d]{%s}\par{\scriptsize %s %d--%d, %s}" % (CL.tex_lang_option(sp), a, b, a, R.base / f, tx(f), a, b, tx(sp["name"]))


def card_tex(R, s, litdir):
    L = [r"\par\medskip\noindent{\large\bfseries \S%s Code: Steps%s}\par" % (s["id"], " and comparison" if s.get("comparison") else " (no comparison)")]
    if s.get("flow"): L.append(r"\par{\small\textbf{Goal of this code as a whole, and why this tool.} %s%s}\par" % (tx(s["flow"]), (r"\par " + tx(s["why"])) if s.get("why") else ""))
    L.append(r"\par\smallskip\noindent\textbf{The code as a whole, with nothing added}\par")
    for st in s["steps"]:
        L += [r"\par\smallskip\noindent\textbf{%s}" % tx(st["title"]), lst(R, (st["file"], st["first"], st["last"]), "", litdir)]
    L.append(r"\par\smallskip\noindent\textbf{The same code with a note above every line}\par")
    for st in s["steps"]:
        L.append(r"\par\smallskip\noindent\textbf{%s}\quad %s\par" % (tx(st["title"]), tx(st["what"])))
        for a, b, text in st["lines"]:
            L += [r"\par\smallskip{\footnotesize\textbf{%s:} %s}" % (("line %d" % a) if a == b else ("lines %d--%d" % (a, b)), tx(text)), lst(R, (st["file"], a, b), "", litdir)]
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
    # panels and cards below fill USED; lang_defs.tex is written at the end
    for s in R.S:
        (out / "panels" / f"p{s['id']}.tex").write_text(panel_tex(R, s) + "\n")
        if s.get("steps"): (out / "codecards" / f"c{s['id']}.tex").write_text(card_tex(R, s, out / "lit") + "\n")
        if s.get("glossary"):
            (out / "glossary").mkdir(exist_ok=True)
            rows = "".join(f"{tx(w)} & {tx(d)} & {tx(wh)} & {tx(fl)} \\\\\n" for w, d, wh, fl in s["glossary"])
            (out / "glossary" / f"g{s['id']}.tex").write_text(r"{\footnotesize\begin{longtable}{@{}p{2.8cm}p{9.2cm}p{1.8cm}p{1.2cm}@{}}\toprule term&explanation and use&where&field\\\midrule\endhead" + "\n" + rows + r"\bottomrule\end{longtable}}" + "\n")
        lt = ledger_auto_tex(R, s)
        if lt:
            (out / "ledger").mkdir(exist_ok=True); (out / "ledger" / f"l{s['id']}.tex").write_text(lt)
        if s.get("bridge"):
            (out / "bridge").mkdir(exist_ok=True); (out / "bridge" / f"br{s['id']}.tex").write_text(r"\par\medskip\noindent{\small\textbf{To the next section.} %s}\par" % tx(s["bridge"]) + "\n")
    (out / "lang_defs.tex").write_text(CL.tex_definitions(sorted(k for k in USED if k)) + "\n")  # \input in the preamble
    if CL.warn_unknown(): print("WARNING: unknown code language (listed without color): " + ", ".join(CL.warn_unknown()))
    print(f"built {len(R.S)} sections -> {out}")


if __name__ == "__main__":
    main()
