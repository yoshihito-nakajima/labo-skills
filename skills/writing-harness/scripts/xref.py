"""Label-based numbers shared by the TeX output and the reading page.

Sections and subsections take their numbers from structure.yaml, fact cards from
`reader.numbering`, and labelled displays from the order in which the paper prints
them. A display `\\[ ... \\label{eq:x} \\]` is printed with `\\tag{N}\\label{eq:x}`,
so the PDF and the reading page show the same N and no number is typed by hand.
`check` warns about numbers that were typed by hand and labels that resolve nowhere.
"""
import re

DISPLAY_RE = re.compile(r'\\\[(.*?)\\\]', re.S)
LABEL_RE = re.compile(r'\\label\{([^}]*)\}')
TAG_RE = re.compile(r'\\tag\*?\{([^}]*)\}')
REF_RE = re.compile(r'\\(ref|eqref|Cref|cref)\{([^}]*)\}')
MATH_RE = re.compile(r'\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)'
                     r'|\\begin\{(equation|align|gather|multline)\*?\}.*?\\end\{\1\*?\}', re.S)
HAND_RE = re.compile(
    r'(?<![\w\\])(?:(?:Sections?|Subsections?|Theorems?|Lemmas?|Propositions?|Definitions?'
    r'|Corollar(?:y|ies)|Remarks?|Examples?|Equations?)(?:~|\s)+\d+(?:\.\d+)*'
    r'|§+\s*\d+(?:\.\d+)*|\(\d+\.\d+\)|(?:定理|補題|命題|定義)\s*\d+(?:\.\d+)*|第\s*\d+\s*節)')


def printed_texts(cards, items, prop_kinds, author_proofs):
    """(section number, anchor, text) in the order the paper prints them; mirrors `render_card`."""
    for si, _, cid, opt in items:
        if opt.get('_subsection') or cid not in cards:
            continue
        c = cards[cid]
        key = 'A' if si is None else str(si + 1)
        if c.kind == 'explanation':
            if c.meta.get('role') != 'proof':
                yield key, cid, c.body
            continue
        if opt.get('_proof_only'):
            yield key, f'{cid}-proof', author_proofs[cid].body if cid in author_proofs else c.sec('Proof')
            continue
        yield key, cid, c.sec('Statement')
        if c.kind in prop_kinds:
            mode = opt.get('proof') or ('author' if cid in author_proofs else 'fact')
            if mode == 'author' and cid in author_proofs:
                yield key, cid, author_proofs[cid].body
            elif mode in ('fact', 'author'):
                yield key, cid, c.sec('Proof')


def equation_numbers(texts):
    """Label -> number for labelled displays, counted per section; a display with its own
    \\tag (a name such as (P)) keeps that name and does not advance the count."""
    nums, anchors, count, last = {}, {}, 0, None
    for key, anchor, text in texts:
        if key != last:
            last, count = key, 0
        for m in DISPLAY_RE.finditer(text or ''):
            labels = LABEL_RE.findall(m.group(1))
            if not labels:
                continue
            tag = TAG_RE.search(m.group(1))
            if tag:
                nums[labels[0]] = tag.group(1)
            else:
                count += 1
                nums[labels[0]] = f'{key}.{count}'
            anchors[labels[0]] = anchor
    return nums, anchors


def unnumbered_sections(st):
    """Indices of sections marked `numbered: false` (e.g. References); keep them after the numbered ones."""
    return {si for si, sec in enumerate(st.get('sections') or []) if sec.get('numbered') is False}


def section_numbers(st):
    """Label -> number for sections and subsections that carry `label:` in structure.yaml."""
    nums = {}
    unnumbered = unnumbered_sections(st)
    for si, sec in enumerate(st.get('sections') or []):
        if si in unnumbered:
            continue
        if sec.get('label'):
            nums[sec['label']] = str(si + 1)
        sub = 0
        for it in sec.get('items') or []:
            if isinstance(it, dict) and 'subsection' in it:
                sub += 1
                if it.get('label'):
                    nums[it['label']] = f'{si + 1}.{sub}'
    return nums


def tag_displays(text, eqnums, tex=True):
    """Give each labelled display its number: `\\tag{N}\\label{..}` in TeX, `\\tag{N}` on the page."""
    def one(m):
        body = m.group(1)
        labels = LABEL_RE.findall(body)
        if not labels or labels[0] not in eqnums or TAG_RE.search(body):
            return m.group(0) if tex else '\\[' + LABEL_RE.sub('', body) + '\\]'
        body = LABEL_RE.sub('', body).rstrip()
        lab = labels[0]
        return f'\\[{body}\n\\tag{{{eqnums[lab]}}}' + (f'\\label{{{lab}}}' if tex else '') + '\n\\]'
    return DISPLAY_RE.sub(one, text)


def ref_text(cmd, kind, n):
    """What \\ref, \\eqref, \\Cref or \\cref prints for a section or an equation."""
    if kind == 'Equation':
        return {'ref': n, 'eqref': f'({n})', 'Cref': f'Equation ({n})', 'cref': f'equation ({n})'}[cmd]
    return {'ref': n, 'eqref': f'({n})', 'Cref': f'{kind} {n}', 'cref': f'{kind.lower()} {n}'}[cmd]


def split_multi(text):
    """\\Cref{a,b} (several labels in one reference) as \\Cref{a} and \\Cref{b}, for the reading page."""
    def one(m):
        labs = [x.strip() for x in m.group(2).split(',') if x.strip()]
        refs = [f'\\{m.group(1)}{{{x}}}' for x in labs]
        return refs[0] if len(refs) == 1 else ', '.join(refs[:-1]) + ' and ' + refs[-1]
    return REF_RE.sub(one, text)


def plain_refs(text, targets):
    """Resolve references to plain text (headings, PDF bookmarks); targets: label -> (kind, number)."""
    def one(m):
        t = targets.get(m.group(2))
        return ref_text(m.group(1), *t) if t else m.group(0)
    return REF_RE.sub(one, split_multi(text))


def hand_numbers(text):
    """Internal numbers typed by hand: theorem, section and equation numbers outside math and
    outside citation locators such as [3, Theorem 2.1], plus numeric \\tag{...}."""
    found = [f'\\tag{{{m.group(1)}}}' for m in TAG_RE.finditer(text) if re.match(r'\d', m.group(1))]
    paras = [p for p in re.split(r'\n\s*\n', text) if not re.match(r'\s*\[\d+\]', p)]  # bibliography entries
    t = MATH_RE.sub(' ', '\n\n'.join(paras))
    t = re.sub(r'\[[^\[\]]*\]', ' ', t)
    return found + [m.group(0).replace('\n', ' ') for m in HAND_RE.finditer(t)]


def warnings(cards, st, known_labels):
    """HANDNUM for numbers typed by hand, UNRESOLVED for references to unknown labels."""
    out, eq_labels = [], set()
    for c in cards.values():
        for m in DISPLAY_RE.finditer(c.body):
            labels = LABEL_RE.findall(m.group(1))
            eq_labels.update(labels)
            if len(labels) > 1:
                out.append(f'{c.id}: one display carries several labels ({", ".join(labels)}); split it')
    known = set(known_labels) | eq_labels | set(section_numbers(st or {}))
    titles = [('structure', sec.get('title') or '') for sec in (st or {}).get('sections') or []]
    titles += [('structure', it['subsection']) for sec in (st or {}).get('sections') or []
               for it in sec.get('items') or [] if isinstance(it, dict) and 'subsection' in it]
    for where, text in [(c.id, c.body) for c in cards.values()] + titles:
        for n in hand_numbers(text):
            out.append(f'HANDNUM {where}: "{n}" is typed by hand; refer by label (\\Cref, \\eqref)')
        for m in REF_RE.finditer(text):
            for lab in m.group(2).split(','):
                if lab.strip() not in known:
                    out.append(f'UNRESOLVED {where}: \\{m.group(1)}{{{lab.strip()}}} matches no label')
    return out
