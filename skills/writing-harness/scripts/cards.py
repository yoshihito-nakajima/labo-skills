#!/usr/bin/env python3
"""Card-based paper harness: ids and facts in cards, prose by the author.

See ../SKILL.md and ../references/cards.md. Every path comes from the harness
directory (the one holding harness.toml), found by --root or by walking up from
the current directory.

    python3 cards.py init DIR          # scaffold a new harness from the template
    python3 cards.py check             # schema, ids, cycles, stale prose, structure
    python3 cards.py status            # status ladder counts and open questions
    python3 cards.py graph             # export the knowledge-dependencies graph
    python3 cards.py render [--sections N] [--out NAME]
    python3 cards.py html              # static card viewer
    python3 cards.py read              # reading page (paper order, large type, comments)
    python3 cards.py impact ID...      # facts and prose to recheck after a change
    python3 cards.py anchor ID         # record current fingerprints in a prose card
    python3 cards.py terms [FILE] [--assumed PROFILE.json]
"""
import argparse
import hashlib
import html as _html
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / 'assets' / 'template'
FACT_KINDS = {'definition', 'theorem', 'proposition', 'lemma', 'corollary'}
PROP_KINDS = FACT_KINDS - {'definition'}
STATUS = ['stated', 'drafted', 'gap-free', 'verified', 'lean']
ROLES = {'motivation', 'proof', 'remark', 'transition', 'intro'}
PROOF_MODES = {'fact', 'author', 'omit', 'appendix'}
ID_RE = re.compile(r'^[a-z][a-z0-9-]*$')
DEFAULT_MATHJAX = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg-full.js'


# ---------------------------------------------------------------- harness location and settings

class Harness:
    def __init__(self, root):
        self.root = Path(root).resolve()
        p = self.root / 'harness.toml'
        self.cfg = tomllib.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
        ws = self.cfg.get('workspace')
        if ws:
            self.workspace = (self.root / ws).resolve()
        else:
            self.workspace = next((d for d in [self.root, *self.root.parents] if (d / '.git').exists()), self.root)

    def path(self, key, default):
        return self.root / (self.cfg.get(key) or default)

    cards_dir = property(lambda s: s.path('cards_dir', 'cards'))
    language = property(lambda s: s.cfg.get('language', 'en'))

    def rel(self, p):
        p = Path(p).resolve()
        try:
            return p.relative_to(self.workspace).as_posix()
        except ValueError:
            return p.as_posix()


def find_root(start=None):
    d = Path(start or Path.cwd()).resolve()
    for c in [d, *d.parents]:
        if (c / 'harness.toml').exists():
            return c
    sys.exit('no harness.toml here or above; pass --root or run `cards.py init DIR`')


# ---------------------------------------------------------------- loading

class Card:
    def __init__(self, path):
        self.path = path
        text = path.read_text(encoding='utf-8')
        m = re.match(r'^---\n(.*?)\n---\n?(.*)$', text, re.S)
        if not m:
            raise ValueError(f'{path.name}: missing YAML front matter')
        self.meta = yaml.safe_load(m.group(1)) or {}
        self.body = m.group(2)
        self.sections = {}
        cur = None
        for line in self.body.splitlines(keepends=True):
            h = re.match(r'^## (.+?)\s*$', line)
            if h:
                cur = h.group(1)
                self.sections[cur] = ''
            elif cur is not None:
                self.sections[cur] += line

    id = property(lambda s: s.meta.get('id'))
    kind = property(lambda s: s.meta.get('kind'))
    is_fact = property(lambda s: s.kind in FACT_KINDS)
    requires = property(lambda s: list(s.meta.get('requires') or []))

    def sec(self, name):
        return self.sections.get(name, '').strip()

    def fingerprint(self):
        norm = ' '.join((self.sec('Statement') + '\n' + self.sec('Proof')).split())
        return hashlib.sha256(norm.encode()).hexdigest()[:8]


def load_cards(h):
    cards, errors = {}, []
    for p in sorted(h.cards_dir.glob('*/*.md')):
        try:
            c = Card(p)
        except Exception as e:  # noqa: BLE001 - report every unreadable card
            errors.append(str(e))
            continue
        if not c.id or not ID_RE.match(str(c.id)):
            errors.append(f'{h.rel(p)}: bad or missing id')
            continue
        if c.id in cards:
            errors.append(f'{h.rel(p)}: duplicate id {c.id}')
            continue
        if p.stem != c.id:
            errors.append(f'{h.rel(p)}: file name differs from id {c.id}')
        cards[c.id] = c
    return cards, errors


def load_structure(h):
    p = h.path('structure', 'structure.yaml')
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.exists() else None


def structure_items(st):
    """Yield (section_index, section_title, card_id, options) in reading order."""
    for i, sec in enumerate(st.get('sections') or []):
        for it in sec.get('items') or []:
            if isinstance(it, str):
                yield i, sec['title'], it, {}
            else:
                it = dict(it)
                cid = it.pop('card')
                yield i, sec['title'], cid, it
    for it in st.get('appendix') or []:
        if isinstance(it, str):
            yield None, 'Appendix', it, {}
        else:
            yield None, 'Appendix', it['card'], {k: v for k, v in it.items() if k != 'card'}


# ---------------------------------------------------------------- checks

def check(h, cards, errors):
    errors, warn = list(errors), []
    for c in cards.values():
        k = c.kind
        if k == 'explanation':
            if c.meta.get('role') not in ROLES:
                errors.append(f'{c.id}: role must be one of {sorted(ROLES)}')
            anchors = c.meta.get('anchors') or {}
            for x in c.meta.get('explains') or []:
                if x not in cards or not cards[x].is_fact:
                    errors.append(f'{c.id}: explains unknown fact card {x}')
                elif x not in anchors:
                    warn.append(f'{c.id}: no anchor for {x} (run anchor)')
                elif anchors[x] != cards[x].fingerprint():
                    warn.append(f'STALE {c.id}: {x} changed since this text was written')
        elif k in FACT_KINDS:
            status = c.meta.get('status')
            if status not in STATUS:
                errors.append(f'{c.id}: status must be one of {STATUS}')
            if not c.sec('Statement'):
                errors.append(f'{c.id}: empty Statement')
            if k in PROP_KINDS and status not in (None, 'stated') and not c.sec('Proof'):
                errors.append(f'{c.id}: status {status} but no Proof')
            lean = c.meta.get('lean')
            if lean is not None and not (isinstance(lean, list) and all(isinstance(x, str) and x for x in lean)):
                errors.append(f'{c.id}: lean must be a list of declaration names')
            if status == 'lean' and not lean:
                errors.append(f'{c.id}: status lean but no lean declarations')
            for r in c.requires:
                if r not in cards:
                    errors.append(f'{c.id}: requires unknown card {r}')
        else:
            errors.append(f'{c.id}: unknown kind {k}')
    # hard cycles among fact cards
    seen, stack, cycles = {}, [], []

    def visit(u):
        seen[u] = 1
        stack.append(u)
        for v in cards[u].requires:
            if v not in cards:
                continue
            if seen.get(v) == 1:
                cycles.append(stack[stack.index(v):] + [v])
            elif v not in seen:
                visit(v)
        stack.pop()
        seen[u] = 2

    for u in sorted(cards):
        if cards[u].is_fact and u not in seen:
            visit(u)
    errors += ['cycle: ' + ' -> '.join(cy) for cy in cycles]
    st = load_structure(h)
    if st:
        pos = {}
        for n, (si, _, cid, opt) in enumerate(structure_items(st)):
            if cid not in cards:
                errors.append(f'structure: unknown card {cid}')
                continue
            if cid in pos:
                errors.append(f'structure: {cid} appears twice')
            pos[cid] = (n, si)
            if opt.get('proof') and opt['proof'] not in PROOF_MODES:
                errors.append(f'structure: {cid}: proof must be one of {sorted(PROOF_MODES)}')
        external = set(st.get('external') or [])
        for cid, (n, _) in pos.items():
            for r in cards[cid].requires:
                if r in external:
                    continue
                if r not in pos:
                    warn.append(f'MISSING {cid} needs {r}, which is not in the structure')
                elif pos[r][0] > n:
                    warn.append(f'FORWARD {cid} uses {r} ({"appendix" if pos[r][1] is None else "later"})')
        unused = sorted(c for c in cards if cards[c].is_fact and c not in pos)
        if unused:
            warn.append(f'UNUSED fact cards ({len(unused)}): ' + ', '.join(unused))
    return errors, warn


# ---------------------------------------------------------------- commands

def cmd_init(a):
    dest = Path(a.dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    clash = [p.name for p in TEMPLATE.iterdir() if (dest / p.name).exists()]
    if clash:
        sys.exit(f'refusing to overwrite in {dest}: {", ".join(sorted(clash))}')
    for p in TEMPLATE.iterdir():
        (shutil.copytree if p.is_dir() else shutil.copy2)(p, dest / p.name)
    for sub in ('def', 'prop', 'expl'):
        (dest / 'cards' / sub).mkdir(parents=True, exist_ok=True)
    print(f'harness created in {dest}')
    return 0


def cmd_check(h, a):
    cards, errors = load_cards(h)
    errors, warn = check(h, cards, errors)
    if a.json:
        print(json.dumps({'cards': len(cards), 'errors': errors, 'warnings': warn}, ensure_ascii=False, indent=1))
    else:
        for w in warn:
            print('warn:', w)
        for e in errors:
            print('error:', e)
        print(f'{len(cards)} cards, {len(errors)} errors, {len(warn)} warnings')
    return 1 if errors else 0


def cmd_status(h, a):
    cards, _ = load_cards(h)
    by = {}
    for c in cards.values():
        if c.is_fact:
            by.setdefault(c.meta.get('status'), []).append(c.id)
    for s in STATUS:
        print(f'{s:9s} {len(by.get(s, [])):3d}')
    print(f'explanations {sum(c.kind == "explanation" for c in cards.values())}')
    qs = [(c.id, c.meta['questions']) for c in cards.values() if c.meta.get('questions')]
    if qs:
        print('\nopen questions:')
        for cid, xs in qs:
            for x in xs:
                print(f'  [{cid}] {x}')
    return 0


def cmd_graph(h, a):
    """Export fact cards to the knowledge-dependencies schema (version 1)."""
    cards, _ = load_cards(h)
    kinds = {'definition': 'definition', 'lemma': 'lemma'}
    nodes = []
    for c in sorted(cards.values(), key=lambda c: c.id):
        if not c.is_fact:
            continue
        nodes.append(dict(id=c.id, kind=kinds.get(c.kind, 'theorem'),
                          statement=' '.join(c.sec('Statement').split()) or c.id,
                          source=dict(path=h.rel(c.path), locator='## Statement and ## Proof'),
                          requires=sorted(set(r for r in c.requires if r in cards))))
    g = dict(schema_version=1, scope='All fact cards of the harness.',
             coverage=dict(status='partial',
                           note='Generated from card requires lists by cards.py graph; edges are as declared in the cards.'),
             nodes=nodes)
    out = h.path('graph', 'dependencies.yaml')
    out.write_text(yaml.safe_dump(g, allow_unicode=True, sort_keys=False, width=100), encoding='utf-8')
    print(f'{len(nodes)} nodes -> {h.rel(out)}')
    return 0


def dependents(cards, seeds):
    rev = {}
    for c in cards.values():
        for r in c.requires:
            rev.setdefault(r, set()).add(c.id)
    out, todo = set(seeds), list(seeds)
    while todo:
        for v in rev.get(todo.pop(), ()):
            if v not in out:
                out.add(v)
                todo.append(v)
    return out


def cmd_impact(h, a):
    cards, _ = load_cards(h)
    for i in a.ids:
        if i not in cards:
            sys.exit(f'unknown card {i}')
    facts = dependents(cards, a.ids)
    ex = sorted(c.id for c in cards.values() if c.kind == 'explanation' and set(c.meta.get('explains') or []) & facts)
    print('facts to recheck:', ', '.join(sorted(facts)))
    print('explanations to reread:', ', '.join(ex) or '-')
    return 0


def cmd_anchor(h, a):
    cards, _ = load_cards(h)
    c = cards.get(a.id)
    if not c or c.kind != 'explanation':
        sys.exit(f'{a.id} is not an explanation card')
    text = c.path.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n?', text, re.S)
    meta = yaml.safe_load(m.group(1))
    meta['anchors'] = {x: cards[x].fingerprint() for x in meta.get('explains') or [] if x in cards}
    c.path.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n' + text[m.end():],
                      encoding='utf-8')
    print(f'{a.id}: anchors', meta['anchors'])
    return 0


# ---------------------------------------------------------------- render

THEOREMS = r"""\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}
"""

HEADS = {
    'en': '% !TeX program = pdflatex\n\\documentclass[11pt]{amsart}\n'
          '\\usepackage{amsmath,amssymb,amsthm,mathtools}\n\\usepackage{enumitem}\n\\usepackage[hidelinks]{hyperref}\n',
    # upLaTeX + dvipdfmx, the usual engine for Japanese mathematical manuscripts
    'ja': '% !TeX program = uplatex\n\\documentclass[uplatex,dvipdfmx,11pt]{jsarticle}\n'
          '\\usepackage{amsmath,amssymb,amsthm,mathtools}\n\\usepackage{enumitem}\n\\usepackage[dvipdfmx,hidelinks]{hyperref}\n',
}


def preamble(h, title):
    if h.cfg.get('preamble'):
        return h.path('preamble', '').read_text(encoding='utf-8').rstrip() + '\n'
    head = HEADS.get(h.language)
    if head is None:
        sys.exit(f'no built-in preamble for language {h.language!r}; set preamble = "FILE" in harness.toml')
    macros = h.path('macros', 'macros.tex')
    extra = macros.read_text(encoding='utf-8') if h.cfg.get('macros') or macros.exists() else ''
    author = h.cfg.get('author', '')
    return head + '\n' + THEOREMS + '\n' + extra + f'\n\\title{{{title}}}\n\\author{{{author}}}\n\\date{{\\today}}\n'


def card_label(c):
    return c.meta.get('label') or f'card:{c.id}'


def link_refs(text, cards):
    """Turn bare card labels and bare card ids in running text into \\ref."""
    labels = {card_label(c) for c in cards.values() if c.is_fact}
    ids = {c.id: c for c in cards.values() if c.is_fact}
    out = re.sub(r'(?<![{A-Za-z0-9_:-])([a-z]+:[a-z0-9-]+)(?![A-Za-z0-9_}-])',
                 lambda m: f'\\ref{{{m.group(1)}}}' if m.group(1) in labels else m.group(0), text)
    for cid in sorted(ids, key=len, reverse=True):
        out = re.sub(r'(?<![{A-Za-z0-9_:-])' + re.escape(cid) + r'(?![A-Za-z0-9_}-])',
                     lambda m, c=ids[cid]: '\\ref{' + card_label(c) + '}', out)
    return out


def _reader():
    sys.path.insert(0, str(SKILL / 'scripts'))
    import reader
    return reader


def render_card(cards, cid, opt, author_proofs):
    c = cards[cid]
    if c.kind == 'explanation':
        return '' if c.meta.get('role') == 'proof' else f'% card {cid}\n{c.body.strip()}\n'
    # braces keep a ']' inside the title (e.g. \cite[...]) out of the optional argument
    title = f'[{{{c.meta["title"]}}}]' if c.meta.get('title') else ''
    out = [f'% card {cid} ({c.meta.get("status")})', f'\\begin{{{c.kind}}}{title}\\label{{{card_label(c)}}}',
           link_refs(_reader().external_steps_display(c.sec('Statement'), opt['_stepped']), cards), f'\\end{{{c.kind}}}']
    if c.kind in PROP_KINDS:
        mode = opt.get('proof') or ('author' if cid in author_proofs else 'fact')
        if mode == 'author' and cid in author_proofs:
            out += ['\\begin{proof}', author_proofs[cid].body.strip(), '\\end{proof}']
        elif mode in ('fact', 'author') and c.sec('Proof'):
            proof = link_refs(_reader().external_steps_display(
                _reader().proof_display(cid, c.sec('Proof'), opt['_stepped']), opt['_stepped']), cards)
            out += [f'% agent reference proof ({cid})', '\\begin{proof}', proof, '\\end{proof}']
        elif mode == 'appendix':
            out += ['\\noindent\\emph{Proof in the appendix.}']
    return '\n'.join(out) + '\n'


def cmd_render(h, a):
    cards, _ = load_cards(h)
    st = load_structure(h)
    if not st:
        sys.exit('no structure.yaml')
    if (a.out or '') == 'main.tex':
        sys.exit('refusing to write main.tex: it would clash with a hand-written root; choose another name')
    author_proofs = {x: c for c in cards.values() if c.kind == 'explanation' and c.meta.get('role') == 'proof'
                     for x in c.meta.get('explains') or []}
    title = st.get('title') or h.cfg.get('title') or 'Draft'
    stepped = _reader().stepped_ids(cards, _reader().step_references(cards))
    body, cur, appendix = [], object(), False
    for si, stitle, cid, opt in structure_items(st):
        if cid not in cards or (a.sections is not None and (si is None or si >= a.sections)):
            continue
        if si is None and not appendix:
            body.append(f'\\appendix\n\\section{{{h.cfg.get("appendix_title", "Deferred proofs")}}}\n')
            appendix = True
        elif si is not None and si != cur:
            body.append(f'\\section{{{stitle}}}\n')
            cur = si
        body.append(render_card(cards, cid, {**opt, '_stepped': stepped}, author_proofs))
    bib = ''
    if h.cfg.get('bibliography'):
        bibfile = h.path('bibliography', '').resolve()
        bib = f'\n\\bibliographystyle{{amsplain}}\n\\bibliography{{{bibfile.with_suffix("").as_posix()}}}\n'
    out = h.path('paper_dir', 'paper') / (a.out or 'cards.tex')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(preamble(h, title) + '\\begin{document}\n\\maketitle\n\n' + '\n'.join(body) + bib + '\\end{document}\n',
                   encoding='utf-8')
    print(f'-> {h.rel(out)}')
    return 0


# ---------------------------------------------------------------- html viewer

def tex_to_html(text, label_map, ids):
    t = _html.escape(text.strip(), quote=False)
    t = re.sub(r'\\label\{[^}]*\}', '', t)

    def ref(m):
        lab = m.group(2)
        cid = label_map.get(lab) or (lab if lab in ids else None)
        return f'<a href="#{cid}">{lab}</a>' if cid else f'<code>{lab}</code>'

    t = re.sub(r'\\(ref|eqref|Cref|cref)\{([^}]*)\}', ref, t)
    for env, tag in (('enumerate', 'ol'), ('itemize', 'ul')):
        t = re.sub(r'\\begin\{' + env + r'\}(\[[^\]]*\])?', f'<{tag}>', t)
        t = t.replace(r'\end{' + env + '}', f'</li></{tag}>')
    t = re.sub(r'<(ol|ul)>\s*\\item', r'<\1><li>', t)
    t = re.sub(r'\\item\b', '</li><li>', t)
    t = re.sub(r'\\emph\{([^{}]*)\}', r'<em>\1</em>', t)
    t = re.sub(r'\\textbf\{([^{}]*)\}', r'<strong>\1</strong>', t)
    t = t.replace('~', ' ')
    for cid in sorted(ids, key=len, reverse=True):
        t = re.sub(r'(?<![A-Za-z0-9_#-])' + re.escape(cid) + r'(?![A-Za-z0-9_-])', f'<a href="#{cid}">{cid}</a>', t)
    return ''.join(f'<p>{x.strip()}</p>' for x in re.split(r'\n\s*\n', t) if x.strip())


def cmd_html(h, a):
    cards, errors0 = load_cards(h)
    st = load_structure(h) or {}
    ids = set(cards)
    label_map = {c.meta['label']: c.id for c in cards.values() if c.meta.get('label')}
    rev, explained = {}, {}
    for c in cards.values():
        for r in c.requires:
            rev.setdefault(r, []).append(c.id)
        if c.kind == 'explanation':
            for x in c.meta.get('explains') or []:
                explained.setdefault(x, []).append(c.id)
    errors, warn = check(h, cards, errors0)
    stale = {w.split()[1].rstrip(':') for w in warn if w.startswith('STALE')}
    order, seen, toc = [], set(), []
    for _, stitle, cid, _ in (structure_items(st) if st else []):
        if cid in cards and cid not in seen:
            if not toc or toc[-1][0] != stitle:
                toc.append((stitle, []))
            toc[-1][1].append(cid)
            order.append(cid)
            seen.add(cid)
    rest = sorted(c for c in cards if c not in seen)
    if rest:
        toc.append(('Not in structure', rest))
        order += rest

    def chip(cid):
        c = cards.get(cid)
        return f'<a class="chip s-{c.meta.get("status", c.kind) if c else "x"}" href="#{cid}">{cid}</a>'

    out = []
    for cid in order:
        c = cards[cid]
        status = c.meta.get('status', 'explanation')
        head = f'<span class="kind">{c.kind}</span> <span class="badge s-{status}">{status}</span>'
        if cid in stale:
            head += ' <span class="badge stale">STALE</span>'
        title = c.meta.get('title') or ''
        meta = []
        if c.meta.get('label'):
            meta.append(f'label <code>{c.meta["label"]}</code>')
        if c.meta.get('source'):
            meta.append(f'source <code>{_html.escape(str(c.meta["source"]))}</code>')
        if c.meta.get('lean'):
            meta.append('lean ' + ' '.join(f'<code>{_html.escape(x)}</code>' for x in c.meta['lean']))
        meta.append(f'file <code>{_html.escape(h.rel(c.path))}</code>')
        if c.is_fact:
            meta.append(f'fingerprint <code>{c.fingerprint()}</code>')
        body = []
        if c.kind == 'explanation':
            body.append(f'<div class="sec expl">{tex_to_html(c.body, label_map, ids)}</div>')
        else:
            for name in ('Statement', 'Proof', 'Shortcuts', 'Notes'):
                if c.sec(name):
                    cls = 'stmt' if name == 'Statement' else name.lower()
                    body.append(f'<div class="sec {cls}"><h4>{name}</h4>{tex_to_html(c.sec(name), label_map, ids)}</div>')
        if c.meta.get('questions'):
            body.append('<div class="sec questions"><h4>Open questions</h4><ul>' +
                        ''.join(f'<li>{_html.escape(str(x))}</li>' for x in c.meta['questions']) + '</ul></div>')
        rel = []
        if c.requires:
            rel.append('uses: ' + ' '.join(chip(x) for x in c.requires))
        if rev.get(cid):
            rel.append('used by: ' + ' '.join(chip(x) for x in sorted(rev[cid])))
        if explained.get(cid):
            rel.append('explained in: ' + ' '.join(chip(x) for x in sorted(explained[cid])))
        if c.kind == 'explanation' and c.meta.get('explains'):
            rel.append('explains: ' + ' '.join(chip(x) for x in c.meta['explains']))
        search = _html.escape((cid + ' ' + title + ' ' + c.body).lower())
        out.append(f'<article id="{cid}" class="card" data-search="{search}">'
                   f'<header><h3>{cid}</h3><div class="title">{_html.escape(title)}</div><div>{head}</div></header>'
                   f'<div class="meta">{" · ".join(meta)}</div>{"".join(body)}<div class="rel">{"<br>".join(rel)}</div></article>')
    nav = ''.join(f'<details open><summary>{_html.escape(t)}</summary>' +
                  ''.join(f'<a class="nav s-{cards[c].meta.get("status", "explanation")}" href="#{c}">{c}</a>' for c in cs) +
                  '</details>' for t, cs in toc)
    counts = {}
    for c in cards.values():
        k = c.meta.get('status', 'explanation')
        counts[k] = counts.get(k, 0) + 1
    summary = ' '.join(f'<span class="badge s-{k}">{k} {v}</span>' for k, v in sorted(counts.items()))
    warn_html = ''.join(f'<li>{_html.escape(w)}</li>' for w in errors + warn)
    macros = json.dumps(h.cfg.get('mathjax_macros') or {})
    links = ' · '.join(f'<a href="{_html.escape(str(l.get("href", "")))}">{_html.escape(str(l.get("text", "")))}</a>'
                       for l in h.cfg.get('html_links') or [])
    page = (PAGE.replace('%TITLE%', _html.escape(st.get('title') or h.cfg.get('title') or 'Cards'))
            .replace('%LANG%', _html.escape(h.language)).replace('%MATHJAX%', _html.escape(h.cfg.get('mathjax', DEFAULT_MATHJAX)))
            .replace('%MACROS%', macros).replace('%LINKS%', f'<p>{links}</p>' if links else '').replace('%NAV%', nav).replace('%CARDS%', '\n'.join(out))
            .replace('%SUMMARY%', summary).replace('%WARN%', f'<ul class="warn">{warn_html}</ul>' if warn_html else ''))
    outp = h.path('html_out', 'html') / 'index.html'
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(page, encoding='utf-8')
    print(f'-> {h.rel(outp)}')
    idx = h.cfg.get('html_index')
    if idx is not None:
        write_html_index(h, outp.parent.parent, idx if isinstance(idx, dict) else {})
    return 0


def write_html_index(h, site, opt):
    """List every sibling viewer (a directory holding index.html) on one page."""
    title = _html.escape(str(opt.get('title', 'Card harness')))
    papers = sorted(d.name for d in site.iterdir() if d.is_dir() and (d / 'index.html').exists())
    items = ''.join(f'<li><a href="{_html.escape(d)}/">{_html.escape(d)}</a></li>' for d in papers)
    back = ''.join(f'<p><a href="{_html.escape(str(l.get("href", "")))}">{_html.escape(str(l.get("text", "")))}</a></p>'
                   for l in opt.get('links') or [])
    out = site / 'index.html'
    out.write_text(f'<!doctype html><html lang="{_html.escape(h.language)}"><meta charset="utf-8">'
                   '<meta name="viewport" content="width=device-width,initial-scale=1">'
                   f'<title>{title}</title><style>body{{font:16px/1.6 system-ui,sans-serif;max-width:700px;'
                   f'margin:40px auto;padding:0 16px}}</style><h1>{title}</h1><ul>{items}</ul>{back}', encoding='utf-8')
    print(f'-> {h.rel(out)} ({len(papers)} viewers)')


PAGE = r"""<!doctype html><html lang="%LANG%"><head><meta charset="utf-8"><title>%TITLE%</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>
MathJax = {tex: {inlineMath: [['$','$'],['\\(','\\)']], displayMath: [['\\[','\\]'],['$$','$$']], processEnvironments: true,
  macros: %MACROS%}, options: {skipHtmlTags: ['script','noscript','style','textarea','code']}};
</script>
<script defer src="%MATHJAX%"></script>
<style>
body{margin:0;font:15px/1.6 system-ui,sans-serif;color:#222;background:#fafafa;display:flex}
nav{position:sticky;top:0;height:100vh;overflow:auto;width:300px;flex:none;background:#fff;border-right:1px solid #ddd;padding:10px;box-sizing:border-box;font-size:13px}
nav a.nav{display:block;padding:1px 6px;color:#333;text-decoration:none;border-left:4px solid #ccc;margin:1px 0}
nav summary{font-weight:600;margin-top:8px;cursor:pointer}
main{flex:1;max-width:900px;padding:16px 28px;min-width:0}
input{width:100%;padding:6px;box-sizing:border-box;margin-bottom:6px}
.card{background:#fff;border:1px solid #ddd;border-radius:8px;padding:12px 18px;margin:16px 0}
.card:target{outline:3px solid #f2b400}
header h3{margin:0;font-family:monospace;font-size:15px} header .title{font-weight:600;font-size:17px}
.kind{color:#666;font-size:12px}.meta{color:#777;font-size:12px;margin:4px 0}
.sec h4{margin:10px 0 2px;font-size:13px;color:#555;text-transform:uppercase;letter-spacing:.05em}
.stmt{background:#f4f8ff;border-left:4px solid #5b8def;padding:2px 12px}
.proof{border-left:4px solid #9ad;padding:2px 12px}.notes,.shortcuts{color:#555;font-size:14px}
.questions{background:#fff7e6;padding:2px 12px}.expl{background:#f3fff3;border-left:4px solid #4caf50;padding:2px 12px}
.rel{margin-top:8px;font-size:13px}.chip{display:inline-block;padding:0 6px;margin:1px;border-radius:10px;background:#eee;color:#333;text-decoration:none;font-family:monospace;font-size:12px}
.badge{padding:1px 8px;border-radius:10px;font-size:12px;background:#eee}.stale{background:#e53935;color:#fff}
.s-stated{border-color:#bbb!important}.badge.s-stated{background:#ddd}
.s-drafted{border-color:#f2b400!important}.badge.s-drafted{background:#ffe08a}
.s-gap-free{border-color:#5b8def!important}.badge.s-gap-free{background:#cfe0ff}
.s-verified{border-color:#43a047!important}.badge.s-verified{background:#c8ecc9}
.s-lean{border-color:#7b1fa2!important}.badge.s-lean{background:#e6c8f0}
.s-explanation{border-color:#4caf50!important}
.warn{color:#b00;font-size:13px}
@media (max-width:700px){body{display:block}nav{position:static;width:auto;height:auto}main{padding:8px 16px}}
</style></head><body>
<nav><input id="q" placeholder="search cards"><div>%SUMMARY%</div>%NAV%</nav>
<main>%LINKS%<h1>%TITLE%</h1>%WARN%%CARDS%</main>
<script>
document.getElementById('q').addEventListener('input', e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.card').forEach(c => c.style.display = c.dataset.search.includes(q) ? '' : 'none');
  document.querySelectorAll('nav a.nav').forEach(a => { const c = document.getElementById(a.getAttribute('href').slice(1)); a.style.display = c && c.style.display === 'none' ? 'none' : ''; });
});
</script></body></html>"""


def cmd_read(h, a):
    """Reading page: the paper in reading order, large type, comments copied to the clipboard."""
    sys.path.insert(0, str(SKILL / 'scripts'))
    import reader
    cards, _ = load_cards(h)
    st = load_structure(h)
    if not st:
        sys.exit('no structure.yaml')
    page = reader.build(h, cards, st, list(structure_items(st)), card_label, PROP_KINDS, FACT_KINDS)
    outp = h.path('html_out', 'html') / 'read.html'
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(page, encoding='utf-8')
    print(f'-> {h.rel(outp)}')
    return 0


# ---------------------------------------------------------------- terms (story harness)

def load_vocab(h):
    p = h.path('vocab', 'vocab.toml')
    return tomllib.loads(p.read_text(encoding='utf-8')).get('term', []) if p.exists() else []


def load_assumed(path):
    """Assumed vocabulary from an exposition-granularity profile.json."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return {str(r['term']).lower() for r in data.get('assumed', []) if r.get('term')}


def classify_terms(h, text, assumed=()):
    used = {}
    for n, line in enumerate(text.splitlines(), 1):
        for t in re.findall(r'\[\[([^\]]+)\]\]', re.sub(r'`[^`]*`', '', line)):
            used.setdefault(t.strip(), []).append(n)
    index = {}
    for v in load_vocab(h):
        for nm in [v.get('name') or v.get('draft', ''), *v.get('aliases', [])]:
            for part in (x.strip() for x in re.split(r'[/,]', nm) if x.strip()):
                index[part.lower()] = v
    groups = {g: [] for g in ('unregistered', 'undecided', 'decided', 'standard', 'assumed')}
    for t, lines in sorted(used.items()):
        v = index.get(t.lower())
        if v is None:
            groups['assumed' if t.lower() in assumed else 'unregistered'].append((t, lines, ''))
        elif v.get('standard') or v.get('kind') == 'standard':
            groups['standard'].append((t, lines, v.get('note', '')))
        elif v.get('decided') or v.get('decided_name'):
            groups['decided'].append((t, lines, v.get('card') or v.get('where', '')))
        else:
            groups['undecided'].append((t, lines, v.get('card') or v.get('where', '')))
    return used, groups


def cmd_terms(h, a):
    """Check every [[term]] in the story file against vocab.toml (and the assumed vocabulary)."""
    text = (h.root / (a.file or 'story.md')).read_text(encoding='utf-8')
    prof = a.assumed or (h.cfg.get('assumed_profile') and h.path('assumed_profile', ''))
    assumed = load_assumed(prof) if prof else set()
    used, groups = classify_terms(h, text, assumed)
    label = {'unregistered': 'unregistered (no definition)', 'undecided': 'name undecided',
             'decided': 'defined / decided', 'standard': 'standard term',
             'assumed': 'assumed by the corpus (exposition-granularity)'}
    if a.json:
        print(json.dumps({g: [{'term': t, 'lines': ls, 'info': i} for t, ls, i in xs] for g, xs in groups.items()},
                         ensure_ascii=False, indent=1))
    else:
        for g, xs in groups.items():
            if xs:
                print(f'[{label[g]}]')
                for t, lines, info in xs:
                    print(f'  {t}  (line {",".join(map(str, lines))})' + (f'  -- {info}' if info else ''))
        print(f'{len(used)} terms; {len(groups["unregistered"])} unregistered, {len(groups["undecided"])} undecided')
    return 1 if groups['unregistered'] else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', help='harness directory (default: nearest harness.toml at or above the cwd)')
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('init').add_argument('dir')
    sp.add_parser('check').add_argument('--json', action='store_true')
    for n in ('status', 'graph', 'html', 'read'):
        sp.add_parser(n)
    p = sp.add_parser('render')
    p.add_argument('--sections', type=int, help='only the first N sections')
    p.add_argument('--out', help='file name under the paper directory (default cards.tex)')
    sp.add_parser('impact').add_argument('ids', nargs='+')
    sp.add_parser('anchor').add_argument('id')
    p = sp.add_parser('terms')
    p.add_argument('file', nargs='?')
    p.add_argument('--assumed', help='exposition-granularity profile.json; its assumed terms are not reported')
    p.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'init':
        return cmd_init(a)
    h = Harness(a.root or find_root())
    return globals()['cmd_' + a.cmd](h, a)


if __name__ == '__main__':
    sys.exit(main())
