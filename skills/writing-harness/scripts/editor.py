"""Local editing server for a harness: `cards.py serve`.

    /            the reading page, built from the current cards on every request, with
                 an edit link on every card, live reload after any change, and comments
                 that can be saved into reviews/comments/
    /cards       every card with kind, status, place in the paper and warnings; new cards
    /edit/<id>   the card file in a text area beside a MathJax preview; save with Ctrl+S

Saving checks that the file still parses and still has its id, refuses to overwrite a
file changed on disk since it was opened (an agent may be editing too), writes it,
reports the check messages for that card, and starts the background build, so the
TeX, PDF, viewer and static reading page follow every save.

The server binds to 127.0.0.1 by default and requires the token printed at start
(kept in a cookie after the first visit) for every request.
"""
import argparse
import hashlib
import html as _html
import json
import re
import secrets
import sys
import threading
from datetime import datetime
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import cards as C
import comment_layer
import pipeline
import reader

L = {
    'ja': {'read': '読む', 'cards': 'カード一覧', 'save': '保存', 'saved': '保存した', 'reload': '開き直す',
           'conflict': 'このカードはディスク上で変更されている．「開き直す」で最新を読み込むか，内容をよそに控えてから開き直してね．',
           'new': '新しいカード', 'create': '作る', 'id': 'id', 'title': '題', 'kind': '種類', 'status': '状態',
           'where': '場所', 'warnings': '警告', 'filter': '絞り込み', 'anchor': '読み直した（anchor を更新）',
           'building': 'ビルド中…', 'built': '出力は最新', 'outdated': '古い出力あり', 'updated': 'カードが更新された．クリックで再読込',
           'savec': 'コメントを保存', 'savedc': '保存した: ', 'impact': '影響', 'facts': '確かめ直す事実',
           'prose': '読み直す文章', 'unsaved': '未保存', 'notinpaper': '（本文に未配置）', 'log': 'ビルドの記録',
           'preview': 'プレビュー'},
    'en': {'read': 'Read', 'cards': 'All cards', 'save': 'Save', 'saved': 'Saved', 'reload': 'Reopen',
           'conflict': 'This card changed on disk. Reopen to load the current file (copy your text elsewhere first if you need it).',
           'new': 'New card', 'create': 'Create', 'id': 'id', 'title': 'Title', 'kind': 'Kind', 'status': 'Status',
           'where': 'Place', 'warnings': 'Warnings', 'filter': 'Filter', 'anchor': 'Reread (update anchors)',
           'building': 'Building…', 'built': 'Outputs up to date', 'outdated': 'Outdated outputs',
           'updated': 'The cards changed. Click to reload', 'savec': 'Save comments', 'savedc': 'Saved: ',
           'impact': 'Impact', 'facts': 'facts to recheck', 'prose': 'prose to reread', 'unsaved': 'unsaved',
           'notinpaper': '(not in the paper)', 'log': 'Build log', 'preview': 'Preview'},
}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


class App:
    def __init__(self, h, build=True, pdf=True):
        self.h, self.build, self.pdf = h, build, pdf
        self.lang = 'ja' if h.language == 'ja' else 'en'
        self.L = L[self.lang]
        self.token = secrets.token_urlsafe(16)
        self.lock = threading.Lock()
        mj = h.cfg.get('mathjax', reader.__dict__.get('DEFAULT_MATHJAX') or
                       'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml-full.js')
        self.mj_dir = None
        if not re.match(r'^[a-z]+:|^/', mj):   # a path relative to the viewer directory
            p = (h.path('html_out', 'html') / mj).resolve()
            self.mj_dir, mj = p.parent, '/_mj/' + p.name
        self.mathjax = mj

    # ------------------------------------------------------------ data

    def state(self):
        cards, errs0 = C.load_cards(self.h)
        st = C.load_structure(self.h) or {}
        items = list(C.structure_items(st)) if st else []
        errors, warn = C.check(self.h, cards, errs0)
        return cards, st, items, errors, warn

    def messages_for(self, cid, errors, warn):
        pat = re.compile(r'(?<![a-z0-9-])' + re.escape(cid) + r'(?![a-z0-9-])')
        return ([('error', e) for e in errors if pat.search(e)] +
                [('warn', w) for w in warn if pat.search(w) and not w.startswith('UNUSED')])

    def card_path(self, cid):
        ps = list(self.h.cards_dir.glob(f'*/{cid}.md'))
        return ps[0] if len(ps) == 1 else None

    # ------------------------------------------------------------ pages

    def page_read(self):
        cards, st, items, _, _ = self.state()
        if not st:
            return self.page_cards()
        h2 = C.Harness(self.h.root)
        h2.cfg = {**self.h.cfg, 'mathjax': self.mathjax}
        page = reader.build(h2, cards, st, items, C.card_label, C.PROP_KINDS, C.FACT_KINDS)
        page = comment_layer.inject(page, self.lang, {'saveUrl': '/api/comments', 'saveLabel': self.L['savec'],
                                                      'savedLabel': self.L['savedc']})
        return page.replace('</body>', READ_OVERLAY.replace('%L%', json.dumps(self.L, ensure_ascii=False)) + '</body>')

    def page_cards(self):
        cards, st, items, errors, warn = self.state()
        num = reader.numbering(cards, items, C.FACT_KINDS)
        where, order = {}, []
        for si, stitle, cid, opt in items:
            if cid in cards and cid not in where and not opt.get('_proof_only'):
                where[cid] = (f'{si + 1}' if si is not None else 'A') + f'. {stitle}'
                order.append(cid)
        order += sorted(c for c in cards if c not in where)
        rows = []
        for cid in order:
            c = cards[cid]
            msgs = self.messages_for(cid, errors, warn)
            badge = ''.join(f'<span class="b {k}">{_html.escape(m.split(":")[0] if k == "warn" else "error")}</span>'
                            for k, m in msgs[:3])
            label = (reader.KIND_NAMES.get(c.kind, c.kind) + ' ' + num.get(cid, '')).strip()
            rows.append(f'<tr data-s="{_html.escape((cid + " " + str(c.meta.get("title") or "") + " " + c.kind).lower())}">'
                        f'<td><a href="/edit/{cid}">{cid}</a></td><td>{_html.escape(label)}</td>'
                        f'<td>{_html.escape(str(c.meta.get("title") or ""))}</td>'
                        f'<td>{_html.escape(str(c.meta.get("status") or c.meta.get("role") or ""))}</td>'
                        f'<td>{_html.escape(where.get(cid, self.L["notinpaper"]))}</td><td>{badge}</td></tr>')
        kinds = ''.join(f'<option>{k}</option>' for k in ['definition', 'theorem', 'proposition', 'lemma', 'corollary', 'explanation'])
        top = '\n'.join(f'<li class="{"err" if k == "error" else ""}">{_html.escape(m)}</li>'
                        for k, m in [('error', e) for e in errors] + [('warn', w) for w in warn])
        body = f'''<form id="new" onsubmit="return mk(event)"><b>{self.L["new"]}</b>
<select name="kind">{kinds}</select> <input name="id" placeholder="{self.L["id"]}" pattern="[a-z][a-z0-9-]*" required>
<input name="title" placeholder="{self.L["title"]}"> <button>{self.L["create"]}</button> <span id="nerr"></span></form>
<p><input id="q" placeholder="{self.L["filter"]}" autofocus></p>
<table><thead><tr><th>{self.L["id"]}</th><th></th><th>{self.L["title"]}</th><th>{self.L["status"]}</th><th>{self.L["where"]}</th><th>{self.L["warnings"]}</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
<details><summary>{self.L["warnings"]} ({len(errors) + len(warn)})</summary><ul>{top}</ul></details>
<script>
document.getElementById('q').oninput=e=>{{const q=e.target.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.style.display=r.dataset.s.includes(q)?'':'none')}};
async function mk(e){{e.preventDefault();const f=new FormData(e.target);const r=await post('/api/new',Object.fromEntries(f));
if(r.ok)location.href=r.url;else document.getElementById('nerr').textContent=r.error;return false}}
</script>'''
        return self.shell(self.L['cards'], body)

    def page_edit(self, cid):
        p = self.card_path(cid)
        if p is None:
            return None
        text = p.read_text(encoding='utf-8')
        body = f'''<div id="ed"><textarea id="src" spellcheck="false">{_html.escape(text)}</textarea>
<div id="pv"><div class="muted">{self.L["preview"]}</div><div id="pvb"></div></div></div>
<div id="msgs"></div>
<script>
const CID={json.dumps(cid)}; let BASE={json.dumps(sha(text))}; let dirty=false;
const src=document.getElementById('src'), st=document.getElementById('sst');
function mark(d){{dirty=d;st.textContent=d?L.unsaved:'';}}
let tm=null; src.addEventListener('input',()=>{{mark(true);clearTimeout(tm);tm=setTimeout(preview,400)}});
async function preview(){{const r=await post('/api/preview',{{id:CID,text:src.value}});
  const b=document.getElementById('pvb'); b.innerHTML=r.html||('<pre class="err">'+esc(r.error||'')+'</pre>');
  if(window.MathJax&&MathJax.typesetPromise){{MathJax.typesetClear([b]);MathJax.typesetPromise([b]).catch(()=>{{}});}}
  showMsgs(r.messages||[], r.impact);}}
function showMsgs(ms, imp){{let h=ms.map(m=>'<li class="'+m[0]+'">'+esc(m[1])+'</li>').join('');
  if(imp)h+='<li>'+L.impact+': '+L.facts+' '+esc(imp.facts.join(', ')||'-')+' / '+L.prose+' '+esc(imp.prose.join(', ')||'-')+'</li>';
  if(ms.some(m=>m[1].startsWith('STALE')))h+='<li><button onclick="anchor()">'+L.anchor+'</button></li>';
  document.getElementById('msgs').innerHTML='<ul>'+h+'</ul>';}}
async function save(){{const r=await post('/api/save',{{id:CID,text:src.value,base:BASE}});
  if(r.conflict){{st.innerHTML=esc(L.conflict)+' <button onclick="location.reload()">'+L.reload+'</button>';return}}
  if(!r.ok){{st.textContent=r.error;return}} BASE=r.base; mark(false); st.textContent=L.saved+' '+r.time; showMsgs(r.messages,r.impact); poll();}}
async function anchor(){{if(dirty){{await save()}} const r=await post('/api/anchor',{{id:CID,base:BASE}});
  if(r.ok){{src.value=r.text;BASE=r.base;mark(false);preview();poll()}}else st.textContent=r.error;}}
document.addEventListener('keydown',e=>{{if((e.ctrlKey||e.metaKey)&&e.key==='s'){{e.preventDefault();save()}}}});
window.addEventListener('beforeunload',e=>{{if(dirty){{e.preventDefault();e.returnValue=''}}}});
document.getElementById('bsave').onclick=save; preview();
</script>'''
        tools = (f'<button id="bsave">{self.L["save"]} (Ctrl+S)</button> <a href="/#{cid}">{self.L["read"]}</a> '
                 f'<span id="sst" class="muted"></span>')
        return self.shell(f'{cid}', body, tools=tools, subtitle=self.h.rel(p))

    def shell(self, title, body, tools='', subtitle=''):
        return (SHELL.replace('%TITLE%', _html.escape(title)).replace('%LANG%', self.lang)
                .replace('%MATHJAX%', _html.escape(self.mathjax))
                .replace('%MACROS%', json.dumps(self.h.cfg.get('mathjax_macros') or {}))
                .replace('%L%', json.dumps(self.L, ensure_ascii=False))
                .replace('%NAV%', f'<a href="/">{self.L["read"]}</a> <a href="/cards">{self.L["cards"]}</a> '
                                  f'<b>{_html.escape(title)}</b> <span class="muted">{_html.escape(subtitle)}</span>')
                .replace('%TOOLS%', tools).replace('%BODY%', body))

    # ------------------------------------------------------------ api

    def preview(self, cid, text):
        p = self.card_path(cid) or (self.h.cards_dir / 'x' / f'{cid}.md')
        try:
            card = C.Card(p, text)
        except Exception as e:  # noqa: BLE001 - shown to the author
            return {'error': f'{type(e).__name__}: {e}'}
        cards, st, items, errors, warn = self.state()
        cards = {**cards, cid: card}
        num = reader.numbering(cards, items, C.FACT_KINDS)
        label_to_id = {C.card_label(c): c.id for c in cards.values() if c.is_fact}
        stepped = reader.stepped_ids(cards, reader.step_references(cards))
        conv = lambda t: reader.tex_to_html(reader.external_steps_display(t, stepped), cards, num, label_to_id, C.card_label)
        if card.kind == 'explanation':
            out = f'<section class="prose">{conv(card.body)}</section>'
        else:
            head = (reader.KIND_NAMES.get(card.kind, str(card.kind)) + ' ' + num.get(cid, '')).strip()
            if card.meta.get('title'):
                head += f'（{_html.escape(str(card.meta["title"]))}）'
            out = f'<article class="card"><header><b>{head}</b></header><div class="stmt">{conv(card.sec("Statement"))}</div>'
            if card.sec('Proof'):
                out += f'<div class="proof"><i>Proof.</i> {conv(reader.proof_display(cid, card.sec("Proof"), stepped))}</div>'
            out += '</article>'
            for name, body in card.sections.items():
                if name not in ('Statement', 'Proof') and body.strip():
                    out += f'<h4>{_html.escape(name)}</h4>{conv(body)}'
        return {'html': out, 'messages': self.messages_for(cid, errors, warn), 'impact': self.impact(cards, cid)}

    def impact(self, cards, cid):
        if cid not in cards or not cards[cid].is_fact:
            return None
        facts = C.dependents(cards, [cid])
        prose = sorted(c.id for c in cards.values() if c.kind == 'explanation' and set(c.meta.get('explains') or []) & facts)
        return {'facts': sorted(facts - {cid}), 'prose': prose}

    def save(self, cid, text, base):
        p = self.card_path(cid)
        if p is None:
            return {'ok': False, 'error': f'unknown card {cid}'}
        with self.lock:
            cur = p.read_text(encoding='utf-8')
            if sha(cur) != base:
                return {'ok': False, 'conflict': True}
            text = text.replace('\r\n', '\n')
            try:
                card = C.Card(p, text)
            except Exception as e:  # noqa: BLE001
                return {'ok': False, 'error': f'not saved: {e}'}
            if card.id != cid:
                return {'ok': False, 'error': f'not saved: the id must stay {cid} (ask the agent to rename a card)'}
            tmp = p.with_suffix('.md.tmp')
            tmp.write_text(text, encoding='utf-8')
            tmp.replace(p)
        cards, _, _, errors, warn = self.state()
        res = {'ok': True, 'base': sha(text), 'time': datetime.now().strftime('%H:%M:%S'),
               'messages': self.messages_for(cid, errors, warn), 'impact': self.impact(cards, cid)}
        if self.build:
            res['build'] = pipeline.request_build(self.h, self.pdf)
        return res

    def anchor(self, cid, base):
        p = self.card_path(cid)
        if p is None or sha(p.read_text(encoding='utf-8')) != base:
            return {'ok': False, 'error': self.L['conflict']}
        C.cmd_anchor(self.h, argparse.Namespace(id=cid))
        text = p.read_text(encoding='utf-8')
        if self.build:
            pipeline.request_build(self.h, self.pdf)
        return {'ok': True, 'text': text, 'base': sha(text)}

    def new(self, kind, cid, title):
        try:
            C.new_card(self.h, kind, cid.strip(), title or '')
        except (ValueError, FileExistsError, FileNotFoundError) as e:
            return {'ok': False, 'error': str(e)}
        return {'ok': True, 'url': f'/edit/{cid.strip()}'}

    def comments(self, text):
        d = self.h.root / 'reviews' / 'comments'
        d.mkdir(parents=True, exist_ok=True)
        p = d / f'{datetime.now():%Y-%m-%d}.md'
        with p.open('a', encoding='utf-8') as f:
            f.write(f'\n## {datetime.now():%H:%M:%S}\n\n{text.strip()}\n')
        return {'ok': True, 'path': self.h.rel(p)}


# ---------------------------------------------------------------- http

def handler(app):
    class H(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def authed(self):
            q = parse_qs(urlparse(self.path).query)
            if q.get('t', [''])[0] == app.token:
                return 'set'
            c = cookies.SimpleCookie(self.headers.get('Cookie', ''))
            return 'ok' if 'wh_token' in c and c['wh_token'].value == app.token else None

        def send(self, code, body, ctype='text/html; charset=utf-8', extra=()):
            data = body.encode('utf-8') if isinstance(body, str) else body
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            for k, v in extra:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            auth = self.authed()
            if not auth:
                return self.send(403, 'open the URL printed by cards.py serve (it carries the token)', 'text/plain')
            path = unquote(urlparse(self.path).path)
            if auth == 'set':
                return self.send(303, '', extra=[('Set-Cookie', f'wh_token={app.token}; HttpOnly; SameSite=Strict; Path=/'),
                                                 ('Location', path)])
            try:
                if path == '/':
                    return self.send(200, app.page_read())
                if path == '/cards':
                    return self.send(200, app.page_cards())
                if path.startswith('/edit/'):
                    page = app.page_edit(path[6:])
                    return self.send(200, page) if page else self.send(404, 'no such card', 'text/plain')
                if path == '/api/state':
                    return self.send(200, json.dumps(pipeline.build_state(app.h), ensure_ascii=False), 'application/json')
                if path.startswith('/_mj/') and app.mj_dir:
                    f = (app.mj_dir / path[5:]).resolve()
                    if f.is_relative_to(app.mj_dir) and f.is_file():
                        ctype = {'.js': 'text/javascript', '.woff': 'font/woff', '.woff2': 'font/woff2'}.get(f.suffix, 'application/octet-stream')
                        return self.send(200, f.read_bytes(), ctype)
                return self.send(404, 'not found', 'text/plain')
            except SystemExit as e:
                return self.send(500, str(e), 'text/plain')

        def do_POST(self):
            if self.authed() != 'ok':
                return self.send(403, '{"ok": false, "error": "no token"}', 'application/json')
            n = int(self.headers.get('Content-Length') or 0)
            try:
                d = json.loads(self.rfile.read(n) or b'{}')
            except ValueError:
                return self.send(400, '{"ok": false}', 'application/json')
            path = urlparse(self.path).path
            fn = {'/api/preview': lambda: app.preview(d['id'], d['text']),
                  '/api/save': lambda: app.save(d['id'], d['text'], d.get('base', '')),
                  '/api/anchor': lambda: app.anchor(d['id'], d.get('base', '')),
                  '/api/new': lambda: app.new(d.get('kind', ''), d.get('id', ''), d.get('title', '')),
                  '/api/comments': lambda: app.comments(d.get('text', ''))}.get(path)
            if fn is None:
                return self.send(404, '{"ok": false}', 'application/json')
            try:
                res = fn()
            except (KeyError, SystemExit) as e:
                res = {'ok': False, 'error': str(e)}
            return self.send(200, json.dumps(res, ensure_ascii=False), 'application/json')

    return H


def serve(h, host='127.0.0.1', port=8765, build=True, pdf=True):
    app = App(h, build=build, pdf=pdf)
    srv = ThreadingHTTPServer((host, port), handler(app))
    shown = 'localhost' if host in ('127.0.0.1', '::1', 'localhost') else host
    print(f'editing {h.rel(h.root)}\n  open http://{shown}:{srv.server_address[1]}/?t={app.token}', flush=True)
    if host not in ('127.0.0.1', '::1', 'localhost'):
        print('  note: listening beyond this machine; anyone with the URL (token) can edit the cards', flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


# ---------------------------------------------------------------- page parts

COMMON_JS = r"""
const L=%L%;
const esc=t=>String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;');
async function post(u,d){const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return r.json()}
let SRC=null;
async function poll(){try{const s=await (await fetch('/api/state')).json();
  const b=document.getElementById('bst'); if(b){b.textContent=s.running?L.building:(s.outdated.length?L.outdated+' ('+s.outdated.length+')':L.built);
    b.title=(s.outdated.join('\n')+'\n\n'+s.log.join('\n')).trim(); b.className=s.running?'run':(s.outdated.length?'bad':'ok');}
  if(SRC&&s.source!==SRC&&window.onSourceChange)window.onSourceChange(); SRC=s.source;}catch(e){}}
setInterval(poll,2000); addEventListener('DOMContentLoaded',poll);
"""

SHELL = r"""<!doctype html><html lang="%LANG%"><head><meta charset="utf-8"><title>%TITLE%</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>MathJax={tex:{inlineMath:[['$','$'],['\\(','\\)']],displayMath:[['\\[','\\]'],['$$','$$']],processEnvironments:true,tags:'ams',macros:%MACROS%},
options:{skipHtmlTags:['script','noscript','style','textarea','code']}};</script>
<script defer src="%MATHJAX%"></script>
<script>""" + COMMON_JS + r"""</script>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1f;--muted:#76736d;--rule:#e2ddd3;--box:#f3f0e8;--accent:#8a5a00;--link:#1f5fa8;--bad:#b3261e;--ok:#2e7d32}
@media (prefers-color-scheme: dark){:root{--bg:#1b1b1d;--fg:#e8e6e1;--muted:#9a968e;--rule:#3a3936;--box:#25242a;--accent:#e0b060;--link:#8ab4f8;--bad:#f28b82;--ok:#81c995}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif}
a{color:var(--link);text-decoration:none}
#top{position:sticky;top:0;z-index:5;display:flex;gap:.8em;align-items:center;flex-wrap:wrap;padding:.4em 1em;background:var(--bg);border-bottom:1px solid var(--rule)}
#top .sp{flex:1} button{font:13px system-ui,sans-serif;padding:.2em .7em;border:1px solid var(--rule);background:var(--box);color:var(--fg);border-radius:4px;cursor:pointer}
.muted{color:var(--muted);font-size:.9em} main{padding:.8em 1em}
#bst{font-size:12px;padding:.1em .5em;border-radius:3px;border:1px solid var(--rule)} #bst.bad{color:var(--bad)} #bst.ok{color:var(--ok)} #bst.run{color:var(--accent)}
#ed{display:grid;grid-template-columns:1fr 1fr;gap:1em;height:calc(100vh - 12em)}
@media (max-width:900px){#ed{grid-template-columns:1fr;height:auto}#src{height:60vh}}
#src{width:100%;height:100%;box-sizing:border-box;font:14px/1.55 ui-monospace,"Cascadia Code",monospace;background:var(--box);color:var(--fg);border:1px solid var(--rule);padding:.6em;tab-size:4}
#pv{overflow:auto;padding:0 .6em;border:1px solid var(--rule);font:17px/1.85 "Noto Serif","Noto Serif JP",serif}
.card{margin:.8em 0;padding:.5em .9em;border-left:4px solid var(--accent);background:var(--box);border-radius:4px}
#msgs li.error,li.err,.err{color:var(--bad)} #msgs li.warn{color:var(--accent)}
table{border-collapse:collapse;width:100%} td,th{border-bottom:1px solid var(--rule);padding:.25em .5em;text-align:left;vertical-align:top}
.b{font-size:11px;padding:0 .4em;margin-right:.3em;border-radius:3px;border:1px solid currentColor}.b.warn{color:var(--accent)}.b.error{color:var(--bad)}
#new{margin:.4em 0 1em} input,select{font:14px system-ui,sans-serif;padding:.15em .4em;background:var(--box);color:var(--fg);border:1px solid var(--rule);border-radius:3px}
#q{width:min(30em,90vw)}
</style></head><body>
<div id="top">%NAV%<span class="sp"></span>%TOOLS% <span id="bst"></span></div>
<main>%BODY%</main>
</body></html>"""

READ_OVERLAY = r"""<style>
#bar .wh{font:13px system-ui,sans-serif} .cid a{color:inherit} .cid a:hover{text-decoration:underline}
#bst{font-size:12px;padding:.1em .5em;border-radius:3px;border:1px solid var(--rule)}
#wh-upd{display:none;position:fixed;top:3em;left:50%;transform:translateX(-50%);z-index:9;font:14px system-ui,sans-serif;padding:.4em 1em;background:var(--accent);color:#fff;border:0;border-radius:4px;cursor:pointer}
</style>
<button id="wh-upd"></button>
<script>""" + COMMON_JS + r"""
(function(){
  document.querySelectorAll('[data-card] > .cid, [data-card] header .cid').forEach(s=>{
    const id=s.closest('[data-card]').dataset.card; s.innerHTML='<a href="/edit/'+id+'" title="edit">✎ '+esc(s.textContent)+'</a>';});
  const bar=document.getElementById('bar'), sp=bar.querySelector('.sp');
  const a=document.createElement('a'); a.href='/cards'; a.className='wh'; a.textContent=L.cards; bar.insertBefore(a,sp);
  const b=document.createElement('span'); b.id='bst'; bar.insertBefore(b,sp.nextSibling);
  const k='wh-scroll:'+location.pathname; const y=sessionStorage.getItem(k);
  if(y!==null){sessionStorage.removeItem(k); addEventListener('load',()=>setTimeout(()=>scrollTo(0,+y),300));}
  const reload=()=>{sessionStorage.setItem(k,scrollY);location.reload()};
  const upd=document.getElementById('wh-upd'); upd.textContent=L.updated; upd.onclick=reload;
  window.onSourceChange=()=>{const busy=document.activeElement&&document.activeElement.tagName==='TEXTAREA'||getSelection().toString();
    if(busy)upd.style.display='block'; else reload();};
})();
</script>"""
