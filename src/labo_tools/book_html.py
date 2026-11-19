"""One static HTML page for a route: cards in reading order, filters and a dependency graph.

The page is a reading aid, regenerated from the cards whenever needed; it is never a master
copy.  MathJax is loaded from a CDN (only the library is fetched, nothing from the cards is sent).
`--slice` cuts out a part: a closure, an impact set, one section, one area or some kinds.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from .book import Book, BookError

MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg-full.js"
NODE_KINDS = ("A1", "A2", "A4", "A5", "A6")


def _slice_ids(book: Book, seq: list, spec: str | None) -> set | None:
    if not spec:
        return None
    kind, _, arg = spec.partition(":")
    ids = {e["id"] for e in seq}
    if kind in ("closure", "impact"):
        if arg not in book.cards:
            raise BookError(f"unknown card in slice: {arg}")
        picked = set(book.closure([arg]) if kind == "closure" else book.impact([arg]))
        picked |= {book.chosen_proof(x) for x in list(picked) if x in book.cards and book.cards[x].kind in ("A1", "A2", "A5")}
        return {x for x in picked if x} & ids
    if kind == "section":
        return {e["id"] for e in seq if str(e["section"]) == arg}
    if kind == "area":
        return {i for i in ids if book.cards[i].meta.get("area") == arg}
    if kind == "kinds":
        want = set(arg.split(","))
        return {i for i in ids if book.cards[i].kind in want}
    raise BookError("slice must be closure:<id>, impact:<id>, section:<n>, area:<name> or kinds:<A1,A2,...>")


def _depths(nodes: list, requires: dict) -> dict:
    memo, active = {}, set()

    def depth(n):
        if n in memo:
            return memo[n]
        if n in active:
            return 0
        active.add(n)
        memo[n] = 1 + max([depth(r) for r in requires.get(n, ()) if r in nodes] or [-1])
        active.discard(n)
        return memo[n]

    return {n: depth(n) for n in nodes}


INDEX_MACROS = re.compile(r"\\(?:label|termat|formulaat|index|phantomsection)(?:\{[^{}]*\})+")


def _text(t: str) -> str:
    t = INDEX_MACROS.sub("", t)  # labels and index registrations are not reading text
    t = _html.escape(t.strip(), quote=False)
    t = re.sub(r"\\emph\{([^{}]*)\}", r"<em>\1</em>", t)
    t = re.sub(r"\\textbf\{([^{}]*)\}", r"<strong>\1</strong>", t)
    return "".join(f"<p>{p.strip()}</p>" for p in re.split(r"\n\s*\n", t) if p.strip())


def build_page(book: Book, route: str, slice_: str | None = None) -> str:
    from .book import check

    data = book.load_route(route)
    seq = book.sequence(data)
    seq = [e for e in seq if e["id"] in book.cards]
    keep = _slice_ids(book, seq, slice_)
    view = [e for e in seq if keep is None or e["id"] in keep]
    res = check(book, route)
    stale = {w.split()[1].rstrip(":") for w in res["warnings"] if w.startswith("STALE")}
    shown = {e["id"] for e in view}
    node_ids = [e["id"] for e in view if book.cards[e["id"]].kind in NODE_KINDS]
    requires = {n: [r for r in book.node_requires(n) if r in node_ids] for n in node_ids}
    depth = _depths(node_ids, requires)
    sec_of = {e["id"]: e["section"] for e in view}
    titles = [s["title"] for s in data["sections"]] + ["Appendix"]
    nodes = [{"id": n, "kind": book.cards[n].kind, "status": book.cards[n].meta.get("status", ""),
              "title": book.cards[n].meta.get("title", ""), "depth": depth[n], "section": sec_of[n],
              "stale": n in stale} for n in node_ids]
    edges = [[r, n] for n in node_ids for r in requires[n]]
    used_by: dict = {}
    for n in node_ids:
        for r in requires[n]:
            used_by.setdefault(r, []).append(n)

    def chip(x):
        return f'<a class="chip" href="#{x}">{x}</a>' if x in shown else f'<span class="chip off">{x}</span>'

    arts, current = [], None
    for e in view:
        c = book.cards[e["id"]]
        if e["section"] != current:
            current = e["section"]
            arts.append(f'<h2 id="sec{current}">{_html.escape(titles[current] if current < len(titles) else "")}</h2>')
        head = (f'<span class="kind">{c.kind} {c.template.name if c.template else ""}'
                f'{" / " + c.meta["variant"] if c.meta.get("variant") else ""}</span> '
                f'<span class="badge s-{c.meta.get("status", "none")}">{c.meta.get("status", "")}</span>')
        if c.id in stale:
            head += ' <span class="badge stale">STALE</span>'
        body = "".join(f'<div class="sec"><h4>{_html.escape(ja)}</h4>{_text(c.sections[k])}</div>'
                       for k, ja, _en in (c.template.required + c.template.optional + (("body", "本文", ""),) if c.template else ())
                       if k in c.sections)
        rel = []
        reqs = book.node_requires(c.id) if c.kind in NODE_KINDS else c.requires
        if reqs:
            rel.append("requires: " + " ".join(chip(x) for x in reqs))
        if used_by.get(c.id):
            rel.append("used by: " + " ".join(chip(x) for x in sorted(used_by[c.id])))
        for key in ("proves", "illustrates", "target"):
            if c.meta.get(key):
                rel.append(f"{key}: " + chip(c.meta[key]))
        if c.meta.get("between"):
            rel.append("between: " + " ".join(chip(x) for x in c.meta["between"]))
        src = "; ".join(f"{s.get('src', '')} {s.get('loc', '')}" for s in c.meta.get("sources") or [] if isinstance(s, dict))
        search = _html.escape((c.id + " " + str(c.meta.get("title", "")) + " " + c.body).lower())
        arts.append(
            f'<article id="{c.id}" class="card k-{c.kind}" data-kind="{c.kind}" data-status="{c.meta.get("status", "")}" '
            f'data-search="{search}"><header><h3>{c.id}</h3><div class="title">{_html.escape(str(c.meta.get("title", "")))}</div>'
            f'<div>{head}</div></header><div class="meta">fingerprint <code>{c.fingerprint()}</code>'
            f'{" · source " + _html.escape(src) if src else ""}</div>{body}<div class="rel">{"<br>".join(rel)}</div></article>')
    kinds = sorted({e_kind for e_kind in (book.cards[e["id"]].kind for e in view)})
    payload = json.dumps({"nodes": nodes, "edges": edges, "sections": titles, "kinds": kinds},
                         ensure_ascii=False).replace("</", "<\\/")
    warn = "".join(f"<li>{_html.escape(w)}</li>" for w in res["errors"] + res["warnings"][:40])
    return (PAGE.replace("%TITLE%", _html.escape(str(data["title"]) + (f" [{slice_}]" if slice_ else "")))
            .replace("%MATHJAX%", MATHJAX).replace("%DATA%", payload).replace("%CARDS%", "\n".join(arts))
            .replace("%WARN%", f'<details><summary>checks ({len(res["errors"])} errors, {len(res["warnings"])} warnings)'
                               f'</summary><ul class="warn">{warn}</ul></details>'))


def write_page(workspace: Path, page: str, name: str | None, out: str | None) -> str:
    if out:
        target = Path(out) if Path(out).is_absolute() else workspace / out
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        return str(target)
    if not name or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise BookError("pass --name <letters-digits-dashes> (written to output/<name>.html) or --out <path>")
    from .build import output_transaction

    with output_transaction(workspace) as output:
        target = output / f"{name}.html"
        if target.is_symlink():
            raise BookError("output path must not be a symlink")
        tmp = output / f".{name}.html.tmp"
        tmp.write_text(page, encoding="utf-8")
        tmp.replace(target)
    return f"output/{name}.html"


PAGE = r"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>%TITLE%</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>MathJax={tex:{inlineMath:[['$','$'],['\\(','\\)']],displayMath:[['\\[','\\]'],['$$','$$']]},options:{skipHtmlTags:['script','noscript','style','textarea','code']}};</script>
<script defer src="%MATHJAX%"></script>
<style>
body{margin:0;font:15px/1.6 system-ui,sans-serif;color:#222;background:#fafafa}
header.top{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid #ddd;padding:8px 16px;display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:13px}
header.top input[type=text]{padding:4px 8px;width:220px}
#graphwrap{background:#fff;border-bottom:1px solid #ddd;overflow:auto;max-height:46vh}
main{max-width:920px;margin:0 auto;padding:12px 24px}
.card{background:#fff;border:1px solid #ddd;border-left-width:6px;border-radius:8px;padding:10px 18px;margin:14px 0}
.card:target{outline:3px solid #f2b400}
.card header h3{margin:0;font:600 14px monospace}.card .title{font-weight:600;font-size:17px}
.kind{color:#666;font-size:12px}.meta{color:#777;font-size:12px;margin:4px 0}
.sec h4{margin:8px 0 0;font-size:12px;color:#555;letter-spacing:.05em}
.k-A1{border-left-color:#5b8def}.k-A2{border-left-color:#e07b39}.k-A3{border-left-color:#9ad}.k-A4,.k-A5{border-left-color:#4caf50}
.k-A6{border-left-color:#7b1fa2}.card[class*=k-B]{border-left-color:#bbb;background:#fbfbf6}
.chip{display:inline-block;padding:0 6px;margin:1px;border-radius:10px;background:#eee;color:#333;text-decoration:none;font:12px monospace}
.chip.off{color:#999;background:#f4f4f4}
.badge{padding:1px 8px;border-radius:10px;font-size:12px;background:#eee}.stale{background:#e53935;color:#fff}
.s-stated{background:#ddd}.s-drafted{background:#ffe08a}.s-self-checked{background:#cfe0ff}.s-independent{background:#c8ecc9}.s-lean{background:#e6c8f0}
.rel{margin-top:6px;font-size:13px}.warn{color:#b00;font-size:12px}
svg text{font:11px monospace;pointer-events:none}svg g.n{cursor:pointer}svg g.n rect{stroke:#555;stroke-width:1}
svg .dim{opacity:.12}svg line{stroke:#888;stroke-width:1}svg line.hl{stroke:#e07b39;stroke-width:2}
</style></head><body>
<header class="top"><b>%TITLE%</b>
<input type="text" id="q" placeholder="search cards">
<span id="kindbox"></span>
<label>graph <select id="mode"><option value="card">cards</option><option value="section">sections</option></select></label>
<label>highlight <select id="hl"><option value="closure">prerequisites</option><option value="impact">dependents</option></select></label>
<button id="clear">clear</button></header>
<div id="graphwrap"><svg id="g"></svg></div>
<main>%WARN%%CARDS%</main>
<script id="data" type="application/json">%DATA%</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const COL={A1:'#cfe0ff',A2:'#fbd9bd',A4:'#c8ecc9',A5:'#c8ecc9',A6:'#e6c8f0'};
const kinds=new Set(D.kinds);
const kb=document.getElementById('kindbox');
D.kinds.forEach(k=>{const l=document.createElement('label');l.innerHTML='<input type="checkbox" checked data-k="'+k+'"> '+k+' ';kb.appendChild(l)});
function visible(c){const q=document.getElementById('q').value.toLowerCase();return kinds.has(c.dataset.kind)&&c.dataset.search.includes(q)}
function refresh(){document.querySelectorAll('.card').forEach(c=>c.style.display=visible(c)?'':'none')}
document.getElementById('q').addEventListener('input',refresh);
kb.addEventListener('change',e=>{const k=e.target.dataset.k;e.target.checked?kinds.add(k):kinds.delete(k);refresh()});
let sel=null;
function reach(start,dir){const adj={};D.edges.forEach(([a,b])=>{const [f,t]=dir==='closure'?[b,a]:[a,b];(adj[f]=adj[f]||[]).push(t)});
 const seen=new Set([start]),st=[start];while(st.length){const x=st.pop();(adj[x]||[]).forEach(y=>{if(!seen.has(y)){seen.add(y);st.push(y)}})}return seen}
function draw(){
 const svg=document.getElementById('g');svg.innerHTML='';const mode=document.getElementById('mode').value;
 let N,E;
 if(mode==='card'){N=D.nodes.map(n=>({id:n.id,label:n.id,depth:n.depth,fill:COL[n.kind]||'#eee',stale:n.stale}));E=D.edges}
 else{const secs=[...new Set(D.nodes.map(n=>n.section))].sort((a,b)=>a-b);
  N=secs.map(s=>({id:'S'+s,label:D.sections[s]+' ('+D.nodes.filter(n=>n.section===s).length+')',depth:0,fill:'#eef',stale:D.nodes.some(n=>n.section===s&&n.stale),sec:s}));
  const es=new Set();D.edges.forEach(([a,b])=>{const sa=D.nodes.find(n=>n.id===a).section,sb=D.nodes.find(n=>n.id===b).section;if(sa!==sb)es.add('S'+sa+'>S'+sb)});
  E=[...es].map(x=>x.split('>'));
  const req={};E.forEach(([a,b])=>(req[b]=req[b]||[]).push(a));const memo={};
  const dp=(n,seen=new Set())=>{if(memo[n]!==undefined)return memo[n];if(seen.has(n))return 0;seen.add(n);return memo[n]=1+Math.max(-1,...(req[n]||[]).map(r=>dp(r,seen)))};
  N.forEach(n=>n.depth=dp(n.id))}
 const layers={};N.forEach(n=>(layers[n.depth]=layers[n.depth]||[]).push(n));
 const W=Math.max(...N.map(n=>n.label.length),6)*6.4+14,X=W+50,Y=30;const pos={};
 Object.keys(layers).forEach(d=>layers[d].forEach((n,i)=>pos[n.id]=[10+d*X,10+i*Y]));
 const wmax=Math.max(0,...Object.values(pos).map(p=>p[0]))+W+20,hmax=Math.max(0,...Object.values(pos).map(p=>p[1]))+Y+10;
 svg.setAttribute('width',wmax);svg.setAttribute('height',hmax);
 let on=null;if(sel){const start=mode==='card'?sel:'S'+(D.nodes.find(n=>n.id===sel)||{}).section;
  const adj={};E.forEach(([a,b])=>{const [f,t]=document.getElementById('hl').value==='closure'?[b,a]:[a,b];(adj[f]=adj[f]||[]).push(t)});
  on=new Set([start]);const st=[start];while(st.length){const x=st.pop();(adj[x]||[]).forEach(y=>{if(!on.has(y)){on.add(y);st.push(y)}})}}
 E.forEach(([a,b])=>{if(!pos[a]||!pos[b])return;const l=document.createElementNS('http://www.w3.org/2000/svg','line');
  l.setAttribute('x1',pos[a][0]+W);l.setAttribute('y1',pos[a][1]+10);l.setAttribute('x2',pos[b][0]);l.setAttribute('y2',pos[b][1]+10);
  if(on){on.has(a)&&on.has(b)?l.setAttribute('class','hl'):l.setAttribute('class','dim')}svg.appendChild(l)});
 N.forEach(n=>{const g=document.createElementNS('http://www.w3.org/2000/svg','g');g.setAttribute('class','n'+(on&&!on.has(n.id)?' dim':''));
  g.innerHTML='<rect x="'+pos[n.id][0]+'" y="'+pos[n.id][1]+'" width="'+W+'" height="20" rx="4" fill="'+n.fill+'"'+(n.stale?' stroke="#e53935" stroke-width="2"':'')+'/><text x="'+(pos[n.id][0]+6)+'" y="'+(pos[n.id][1]+14)+'">'+n.label.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</text>';
  g.addEventListener('click',()=>{if(mode==='card'){sel=n.id;location.hash=n.id}else{sel=(D.nodes.find(x=>x.section===n.sec)||{}).id}draw()});svg.appendChild(g)});
}
document.getElementById('mode').addEventListener('change',()=>{sel=null;draw()});
document.getElementById('hl').addEventListener('change',draw);
document.getElementById('clear').addEventListener('click',()=>{sel=null;draw()});
draw();
</script></body></html>
"""
