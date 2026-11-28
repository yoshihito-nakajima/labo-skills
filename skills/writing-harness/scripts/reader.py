"""Reading page for a harness: the paper in reading order, large type, comments to the clipboard.

Called by `cards.py read`. One static HTML file; MathJax renders the TeX. The author
selects text, attaches a comment, and copies all comments (with card ids and the
quoted text) to paste back to the agent. Comments live only in this browser tab.
"""
import html as _html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from labo_tools.reading_page import DEFAULT_MATHJAX, render_reading_page

import xref

KIND_NAMES = {'definition': 'Definition', 'theorem': 'Theorem', 'proposition': 'Proposition',
              'lemma': 'Lemma', 'corollary': 'Corollary', 'remark': 'Remark'}


def numbering(cards, items, fact_kinds):
    """Paper numbers: section.counter with one shared counter per section, A.n in the appendix."""
    num, sec_no, count, last, app = {}, 0, 0, object(), 0
    for si, _, cid, opt in items:
        if opt.get('_appendix_section'):
            app, last, count = app + 1, ('appendix', app + 1), 0
            continue
        if cid not in cards or opt.get('_proof_only'):
            continue
        key = ('appendix', max(app, 1)) if si is None else si
        if key != last:
            last = key
            count = 0
            if si is not None:
                sec_no = si + 1
        if cards[cid].kind in fact_kinds:
            count += 1
            num[cid] = f'{chr(64 + max(app, 1)) if si is None else sec_no}.{count}'
    return num


def tex_to_html(text, cards, num, label_to_id, card_label, targets=None):
    t = _html.escape(text.strip(), quote=False)
    t = re.sub(r'\\paragraph\{([^{}]*)\}', r'<strong class="para">\1</strong>', t)
    t = re.sub(r'\\emph\{([^{}]*)\}', r'<em>\1</em>', t)
    t = re.sub(r'\\textbf\{([^{}]*)\}', r'<strong>\1</strong>', t)

    def ref(m):
        cmd, lab = m.group(1), m.group(2)
        cid = label_to_id.get(lab) or (lab if lab in cards else None)
        if cid and cid in num:
            return f'<a class="ref" href="#{cid}">{KIND_NAMES[cards[cid].kind]} {num[cid]}</a>'
        if lab in (targets or {}):
            kind, n, href = targets[lab]
            return f'<a class="ref" href="#{href}">{xref.ref_text(cmd, kind, n)}</a>'
        return m.group(0)

    t = xref.REF_RE.sub(ref, xref.split_multi(t))
    t = re.sub(r'\\cite\[([^\]]*)\]\{([^}]*)\}', r'<span class="cite">[\2, \1]</span>', t)
    t = re.sub(r'\\cite\{([^}]*)\}', r'<span class="cite">[\1]</span>', t)
    for env, tag in (('enumerate', 'ol'), ('itemize', 'ul')):
        t = re.sub(r'\\begin\{' + env + r'\}(\[[^\]]*\])?', f'<{tag}>', t)
        t = t.replace(r'\end{' + env + '}', f'</li></{tag}>')
    # An item with its own label, \item[(a)], replaces the list number, as in LaTeX.
    li = lambda lab: '<li class="lab"><b>' + lab[1:-1] + '</b> ' if lab else '<li>'
    t = re.sub(r'<(ol|ul)>\s*\\item(\[[^\]]*\])?', lambda m: f'<{m.group(1)}>' + li(m.group(2)), t)
    t = re.sub(r'\\item(\[[^\]]*\])?', lambda m: '</li>' + li(m.group(1)), t)
    t = t.replace('~', ' ')
    for cid in sorted(num, key=len, reverse=True):
        t = re.sub(r'(?<![A-Za-z0-9_#/-])' + re.escape(cid) + r'(?![A-Za-z0-9_-])',
                   f'<a class="ref" href="#{cid}">{KIND_NAMES[cards[cid].kind]} {num[cid]}</a>', t)
    # one paragraph per blank line; proof steps "(n) " start their own paragraph
    t = re.sub(r'\n\((\d+)\) ', r'\n\n(\1) ', t)
    return ''.join(f'<p>{x.strip()}</p>' for x in re.split(r'\n\s*\n', t) if x.strip())


STEP_RE = re.compile(r'(?m)^\((\d+)\)[ \t]*')
EXT_STEP_RE = re.compile(r'([a-z][a-z0-9-]*)([ \t]*(?:の証明|proof)[ \t]*)\((\d+)\)')


MATH_RE = re.compile(r'\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]|\\begin\{(equation|align|gather|multline)\*?\}.*?\\end\{\1\*?\}', re.S)


def _outside_math(text):
    """Spans of text outside inline and display math."""
    pos = 0
    for m in MATH_RE.finditer(text):
        yield pos, m.start()
        pos = m.end()
    yield pos, len(text)


def _sub_outside_math(pattern, repl, text):
    out, pos = [], 0
    for m in MATH_RE.finditer(text):
        out.append(re.sub(pattern, repl, text[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(re.sub(pattern, repl, text[pos:]))
    return ''.join(out)


def step_references(cards):
    """Step numbers of each card's proof that other cards cite as "<id>の証明 (k)" / "<id> proof (k)"."""
    ext = {}
    for c in cards.values():
        for m in EXT_STEP_RE.finditer(c.body):
            ext.setdefault(m.group(1), set()).add(m.group(3))
    return ext


def stepped_ids(cards, ext):
    """Cards whose proof steps are referenced and therefore displayed as "Step k"."""
    out = set()
    for c in cards.values():
        if not c.is_fact:
            continue
        proof = c.sec('Proof')
        steps = set(STEP_RE.findall(proof))
        internal = {m.group(1) for a, b in _outside_math(proof)
                    for m in re.finditer(r'\((\d+)\)', proof[a:b]) if a + m.start() and proof[a + m.start() - 1] != '\n'}
        if steps & (internal | ext.get(c.id, set())):
            out.add(c.id)
    return out


def proof_display(cid, proof, stepped):
    """Working labels "(k)" open proof paragraphs in the cards. On display they are dropped,
    unless some step is referenced: then they read "Step k" and so do the references."""
    proof = re.sub(r'\n\((\d+)\)', r'\n\n(\1)', proof)
    steps = set(STEP_RE.findall(proof))
    if not steps:
        return proof
    if cid not in stepped:
        return STEP_RE.sub('', proof)
    proof = _sub_outside_math(r'(?<=[^\n])\((\d+)\)', lambda m: f'Step {m.group(1)}' if m.group(1) in steps else m.group(0), proof)
    return STEP_RE.sub(lambda m: f'\\emph{{Step {m.group(1)}.}} ', proof)


def external_steps_display(text, stepped):
    """"<id>の証明 (k)" becomes "<id>の証明のStep k" when that proof displays its steps."""
    def sub(m):
        if m.group(1) not in stepped:
            return m.group(0)
        mid = m.group(2)
        return m.group(1) + mid.rstrip() + ('の' if 'の証明' in mid else ' ') + f'Step {m.group(3)}'
    return EXT_STEP_RE.sub(sub, text)


def build(h, cards, st, items, card_label, prop_kinds, fact_kinds):
    num = numbering(cards, items, fact_kinds)
    label_to_id = {card_label(c): c.id for c in cards.values() if c.is_fact}
    author_proofs = {x: c for c in cards.values() if c.kind == 'explanation' and c.meta.get('role') == 'proof'
                     for x in c.meta.get('explains') or []}
    stepped = stepped_ids(cards, step_references(cards))
    eqnums, eqanchors = xref.equation_numbers(xref.printed_texts(cards, items, prop_kinds, author_proofs))
    targets = {lab: ('Section', n, 'sec-' + n.replace('.', '-')) for lab, n in xref.section_numbers(st).items()}
    targets.update({lab: ('Equation', n, eqanchors[lab]) for lab, n in eqnums.items()})
    plain = {lab: (k, n) for lab, (k, n, _) in targets.items()}
    plain.update({card_label(cards[c]): (KIND_NAMES[cards[c].kind], n) for c, n in num.items()})
    heading = lambda s: _html.escape(xref.plain_refs(s, plain))  # noqa: E731
    conv = lambda s: tex_to_html(xref.tag_displays(external_steps_display(s, stepped), eqnums, tex=False),  # noqa: E731
                                 cards, num, label_to_id, card_label, targets)
    out, toc, cur, appendix = [], [], object(), False
    unnumbered = xref.unnumbered_sections(st)
    sub = 0
    for si, stitle, cid, opt in items:
        if opt.get('_subsection'):
            if si != cur:
                cur = si
                out.append(f'<h2 id="sec-{si + 1}">{si + 1}　{heading(stitle)}</h2>')
                toc.append((f'sec-{si + 1}', f'{si + 1}　{heading(stitle)}'))
                sub = 0
            sub += 1
            out.append(f'<h3 id="sec-{si + 1}-{sub}">{si + 1}.{sub}　{heading(opt["_subsection"])}</h3>')
            toc.append((f'sec-{si + 1}-{sub}', f'{si + 1}.{sub}　{heading(opt["_subsection"])}'))
            continue
        if cid not in cards:
            continue
        c = cards[cid]
        if si is None and not appendix:
            appendix = True
            out.append('<h2 id="sec-A">A　{{appendix}}</h2>')
            toc.append(('sec-A', 'A　{{appendix}}'))
        elif si is not None and si != cur:
            cur = si
            sub = 0
            no = '' if si in unnumbered else f'{si + 1}　'
            out.append(f'<h2 id="sec-{si + 1}">{no}{heading(stitle)}</h2>')
            toc.append((f'sec-{si + 1}', f'{no}{heading(stitle)}'))
        if opt.get('_proof_only'):
            proof = (author_proofs[cid].body if cid in author_proofs
                     else proof_display(cid, c.sec('Proof'), stepped))
            name = '{proof}'
            out.append(f'<article id="{cid}-proof" class="card k-proof" data-card="{cid}"><header>'
                       f'<span class="kname"><a href="#{cid}">{KIND_NAMES[c.kind]} {num.get(cid, "")}</a></span>'
                       f'<span class="cid">{cid}</span></header>'
                       f'<details class="proof" open><summary>{name}</summary>{conv(proof)}</details></article>')
            continue
        if c.kind == 'explanation':
            if c.meta.get('role') == 'proof':
                continue
            out.append(f'<section id="{cid}" class="prose" data-card="{cid}"><span class="cid">{cid}</span>{conv(c.body)}</section>')
            continue
        title = f'（{_html.escape(c.meta["title"])}）' if c.meta.get('title') else ''
        head = f'<span class="kname">{KIND_NAMES[c.kind]} {num.get(cid, "")}</span>{title}'
        parts = [f'<div class="stmt">{conv(c.sec("Statement"))}</div>']
        if c.kind in prop_kinds:
            mode = opt.get('proof') or ('author' if cid in author_proofs else 'fact')
            proof = (author_proofs[cid].body if mode == 'author' and cid in author_proofs
                     else proof_display(cid, c.sec('Proof'), stepped))
            if mode in ('fact', 'author') and proof.strip():
                parts.append(f'<details class="proof"><summary>{{{{proof}}}}</summary>{conv(proof)}</details>')
        out.append(f'<article id="{cid}" class="card k-{c.kind}" data-card="{cid}">'
                   f'<header>{head}<span class="cid">{cid}</span></header>{"".join(parts)}</article>')
    nav = ''.join(f'<a href="#{a}">{t}</a>' for a, t in toc)
    title = _html.escape(st.get('title') or h.cfg.get('title') or 'Draft')
    return render_reading_page(title, h.language, nav, '\n'.join(out),
                               macros=h.cfg.get('mathjax_macros'),
                               mathjax=h.cfg.get('mathjax', DEFAULT_MATHJAX),
                               font_px=h.cfg.get('reader_font_px', 21),
                               width_em=h.cfg.get('reader_width_em', 34))
