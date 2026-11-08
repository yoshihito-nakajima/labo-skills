"""Shared loading and validation for reading-companion specs (used by build and check).

Spec shape (paths relative to the spec's directory):
  title, lang, paper{citation, main_figures}, note{pdf, aux}, background{picture, summary, question, context, terms, figure?},
  lineage{families[], entries[] (earlier works: made for, weakness, kept/changed, verified, note labels), after[]?},
  overview[steps], methods{author, prior[]}, datasets[], requests[], figures[] (main-text figures in order),
  features[] (step units: the supplement that reads the code from step 1).
"""
import base64, hashlib, itertools, json, mimetypes, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'deck-from-references', 'scripts'))
from link_note import read_aux, printed  # noqa: E402

PROVENANCE = {'author-code run', 'earlier-method run', 'AI re-implementation'}
LEVELS = ('L1', 'L2', 'L3', 'L4')
RELATIONS = ('same', 'changed', 'author-only', 'prior-only')


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip()) or v == [] or v == {}


def vstr(v):
    return v if isinstance(v, str) else json.dumps(v)


def na(v):
    return isinstance(v, str) and v.startswith('n/a:') and len(v) >= 6


def grid_keys(params):
    if not params:
        return ['default']
    names = [p['name'] for p in params]
    vals = [[vstr(v) for v in p['grid']] for p in params]
    return ['|'.join(f'{n}={v}' for n, v in zip(names, combo)) for combo in itertools.product(*vals)]


def excerpt(root, spec_code):
    path = os.path.join(root, spec_code['file'])
    lines = open(path, encoding='utf-8').read().split('\n')
    first, last = spec_code['first'], spec_code['last']
    text = '\n'.join(lines[first - 1:last])
    return path, lines, text, hashlib.sha256(text.encode()).hexdigest()


def embed_crop(fig, rel, problem):
    """Check a figure entry (paper locator, crop or reason) and embed the crop as a data URI."""
    fig = dict(fig)
    if blank(fig.get('paper_locator')):
        problem('figure needs the paper figure locator')
    crop = fig.get('paper_crop')
    if crop:
        if os.path.exists(rel(crop)):
            mime = mimetypes.guess_type(crop)[0] or 'image/png'
            fig['paper_crop_data'] = f'data:{mime};base64,' + base64.b64encode(open(rel(crop), 'rb').read()).decode()
        else:
            problem(f'paper crop not found: {crop} (report it; do not replace it)')
    elif blank(fig.get('paper_crop_absent')):
        problem('no paper crop and no paper_crop_absent reason')
    return fig


def in_range(rng, c):
    return isinstance(rng, list) and len(rng) == 2 and c.get('first', 0) <= rng[0] <= rng[1] <= c.get('last', 0)


def note_links(keys, labels, lang, P):
    out = []
    for key in keys or []:
        if labels and key not in labels:
            P(f'note label {key!r} not in the note .aux')
        elif key in labels:
            num, page = labels[key]
            out.append({'key': key, 'text': printed(key, num, lang), 'page': page})
    return out


def check_params(params, slot, c, lines, fterms, P):
    for p in params:
        if not any(p.get('name', '\0') in t.get('term', '') for t in fterms):
            P(f"{slot} param {p.get('name')}: not defined in the unit's terms (define before use)")
        if not p.get('data') and (blank(p.get('label')) or p.get('name', '\0') not in p.get('label', '')):
            P(f"{slot} param {p.get('name')}: label (the control's name: the code's argument and what it sets "
              f"in the paper's terms) is missing or does not contain the argument")
        dv = p.get('derives')
        if dv is not None:
            if blank(dv.get('name')) or blank(dv.get('key')):
                P(f"{slot} param {p.get('name')}: derives needs name (the paper's symbol) and key (in the results)")
            elif not any(dv['name'] in t.get('term', '') for t in fterms):
                P(f"{slot} param {p.get('name')}: derived symbol {dv['name']!r} not defined in the unit's terms")
        if p.get('data'):
            # a property of the synthetic data (not an argument of the code): no code line; say what it is
            if blank(p.get('effect')) or p.get('default') not in p.get('grid', []):
                P(f"{slot} data control {p.get('name')}: needs effect and a default in its grid")
            continue
        ln = p.get('line', 0)
        if not (c['first'] <= ln <= c['last']):
            P(f"{slot} param {p.get('name')}: line {ln} outside the excerpt")
        elif p.get('token', '\0') not in lines[ln - 1]:
            P(f"{slot} param {p.get('name')}: token {p.get('token')!r} not on line {ln}")
        if p.get('default') not in p.get('grid', []):
            P(f"{slot} param {p.get('name')}: default not in grid")
        if p.get('stated_in') not in ('paper', 'code'):
            P(f"{slot} param {p.get('name')}: stated_in must be 'paper' or 'code'")
        if blank(p.get('effect')):
            P(f"{slot} param {p.get('name')}: missing effect")


def check_presets(presets, params, what, P):
    byname = {p['name']: p for p in params}
    if byname and blank(presets):
        P(f'no {what} (name values, including extreme ones, and what should visibly change)')
    for pr in presets or []:
        if blank(pr.get('label')) or blank(pr.get('expect')) or blank(pr.get('values')):
            P(f"{what} {pr.get('label')!r}: needs label, values and expect")
            continue
        for n, v in pr['values'].items():
            if n not in byname:
                P(f"{what} {pr['label']!r}: unknown parameter {n!r}")
            elif vstr(v) not in [vstr(g) for g in byname[n].get('grid', [])]:
                P(f"{what} {pr['label']!r}: {n}={v} is not a grid point")


def check_run_card(rc, ac, pc, step_ids, P):
    """What was run: calls (whose code), the flow from each control to the drawing, and where in the method."""
    if not isinstance(rc, dict):
        P('missing run_card (calls, flow, steps, not_run): say what was run')
        return
    calls = rc.get('calls') or []
    if blank(calls):
        P('run_card: no calls')
    for i, c in enumerate(calls):
        if blank(c.get('code')) or blank(c.get('where')) or c.get('by') not in ('author', 'earlier', 'AI'):
            P(f"run_card call {i + 1}: needs code, where and by ('author', 'earlier' or 'AI')")
    if not any(c.get('by') == 'author' for c in calls):
        P("run_card: no call of the authors' code")
    flows = rc.get('flow') or []
    for side, cc in (('author', ac), ('prior', pc)):
        for p in (cc.get('params', []) if isinstance(cc, dict) else []):
            fl = [x for x in flows if x.get('control') == p['name'] and x.get('side', 'author') == side]
            if p.get('data'):
                continue
            if not fl:
                P(f"run_card: no flow for the {side} control {p['name']} (argument → line → output → drawn)")
            for x in fl:
                for k in ('argument', 'output', 'drawn'):
                    if blank(x.get(k)):
                        P(f"run_card flow {p['name']}: missing {k}")
                ln = x.get('line', 0)
                if not (cc.get('first', 0) <= ln <= cc.get('last', 0)):
                    P(f"run_card flow {p['name']}: line {ln} outside the {side} excerpt (the line is re-shown next to the run)")
    st = rc.get('steps') or []
    if blank(st) or any(x not in step_ids for x in st):
        P('run_card: steps must list the overview steps the run executes')
    if blank(rc.get('not_run')):
        P('run_card: not_run (which steps or panels the run does not execute) is missing')


def check_role(r, rel, P):
    """A run says what it is: a remake of named panels (with the panel's crop) or a run for reading the code."""
    r = dict(r or {})
    role = r.get('role')
    if role == 'remake':
        if blank(r.get('panels')) or blank(r.get('compare')):
            P("run role 'remake' needs panels (the paper's panel names) and compare (what to compare)")
        if blank(r.get('panel_figure')):
            P("run role 'remake' needs panel_figure: the crop of exactly those panels")
        else:
            r['panel_figure'] = embed_crop(r['panel_figure'], rel, P)
    elif role == 'demo':
        for k in ('shows', 'truth'):
            if blank(r.get(k)):
                P(f"run role 'demo' needs {k} (what the synthetic experiment shows; the known truth)")
    elif role == 'code':
        if blank(r.get('shows')):
            P("run role 'code' needs shows (what the run shows about the code; it is not a figure of the paper)")
    else:
        P("run needs role: 'remake' (of named panels), 'code' (for reading the code) or 'demo' (synthetic experiment)")
    return {k: r[k] for k in ('role', 'panels', 'compare', 'panel_figure', 'shows', 'truth', 'values_note') if k in r}


def check_code_map(cm, impls, rel, step_ids, P):  # P(what)
    """The entry function's code split into step blocks; other steps' functions listed after it."""
    if not isinstance(cm, dict):
        P('missing code_map (the whole code of the entry function, coloured by step)')
        return None
    ent = cm.get('entry') or {}
    impl = impls.get(ent.get('impl', 'author')) or {}
    try:
        _, lines, text, _ = excerpt(rel(impl.get('root', '')), ent)
    except (OSError, KeyError) as e:
        P(f'cannot read the entry function ({e})')
        return None
    blocks = cm.get('blocks') or []
    pos = ent['first']
    for b in blocks:
        if blank(b.get('text')) or (b.get('step') is not None and b.get('step') not in step_ids):
            P(f"block {b.get('first')}-{b.get('last')}: needs text and a step id of the overview (or null for bookkeeping)")
        f, l = b.get('first', 0), b.get('last', 0)
        if f < pos or l < f or l > ent['last']:
            P(f'block {f}-{l} overlaps the previous block or leaves the entry function')
            continue
        gap = [n for n in range(pos, f) if lines[n - ent['first']].strip() and not lines[n - ent['first']].strip().startswith('#')]
        if gap:
            P(f'lines {gap[0]}-{gap[-1]} are in no block (give them a block)')
        pos = l + 1
    rest = [n for n in range(pos, ent['last'] + 1) if lines[n - ent['first']].strip() and not lines[n - ent['first']].strip().startswith('#')]
    if rest:
        P(f'lines {rest[0]}-{rest[-1]} at the end are in no block')
    used = {b.get('step') for b in blocks} | {x.get('step') for x in cm.get('extra') or []}
    for sid in step_ids:
        if sid not in used:
            P(f'step {sid!r} has no block (put the function that carries it in extra)')
    extra = []
    for x in cm.get('extra') or []:
        im = impls.get(x.get('impl', 'author')) or {}
        try:
            _, _, t, _ = excerpt(rel(im.get('root', '')), x)
        except (OSError, KeyError) as e:
            P(f"extra {x.get('name')}: cannot read ({e})")
            continue
        extra.append(dict(x, text=t))
    return dict(cm, entry=dict(ent, text=text, impl_name=impl.get('name'), commit=impl.get('commit'), license=impl.get('license')), extra=extra)


def check_called(f, impls, rel, P):
    """The whole code of the functions a run calls (the ones whose arguments are controls), shown folded in the run,
    and the selling-point ranges to highlight in it. called: [{impl, name, file, first, last}]; sell: [{file, first, last, label, step?}]."""
    out = []
    for c in f.get('called') or []:
        im = impls.get(c.get('impl')) or {}
        if blank(c.get('name')) or not im:
            P(f"called {c.get('name')!r}: needs name and impl (a method id)"); continue
        try:
            _, _, t, _ = excerpt(rel(im.get('root', '')), c)
        except (OSError, KeyError, ValueError) as e:
            P(f"called {c.get('name')}: cannot read ({e})"); continue
        out.append(dict(c, text=t, repo=im.get('repo'), url=im.get('url'), commit=im.get('commit'), license=im.get('license'), impl_name=im.get('name')))
    sell = []
    for s in f.get('sell') or []:
        if blank(s.get('label')) or not all(isinstance(s.get(k), int) for k in ('first', 'last')):
            P('sell needs label, file, first and last'); continue
        if not any(os.path.basename(c['file']) == os.path.basename(s.get('file', '')) and c['first'] <= s['first'] <= s['last'] <= c['last'] for c in out):
            P(f"sell {s.get('file')} L{s['first']}-{s['last']} is not inside any called function's code")
            continue
        sell.append(s)
    return out, sell


def check_where(where, impls, rel, P):
    """'file L12-30' references in a 'where' string must exist in a method's files (the line is not beyond the file's end)."""
    import re
    for fname, a, b in re.findall(r'([\w./-]+\.\w+)\s+L(\d+)(?:[–-](\d+))?', where or ''):
        found = None
        for m in impls.values():
            root = rel(m.get('root', '.'))
            for dp, _, fs in os.walk(root):
                if os.path.basename(fname) in fs:
                    found = os.path.join(dp, os.path.basename(fname)); break
            if found: break
        if not found:
            P(f'where: {fname} not found under any method root'); continue
        n = sum(1 for _ in open(found, encoding='utf-8', errors='replace'))
        if int(b or a) > n:
            P(f'where: {fname} L{a}-{b or a} is beyond the file ({n} lines)')


def check_lineage(lin, labels, lang, P):
    """The Summary/Introduction history: families of earlier methods and one entry per earlier work."""
    if blank(lin):
        P('missing lineage (earlier methods before any code: what each was made for, its weakness, what the method keeps or changes)')
        return None
    lin = dict(lin)
    for i, fa in enumerate(lin.get('families') or []):
        for k in ('family', 'good', 'weak'):
            if blank(fa.get(k)):
                P(f'family {i + 1}: missing {k}')
    ents = lin.get('entries') or []
    if blank(ents):
        P('no entries (one per earlier work the paper inherits from, compares with or criticises)')
    out = []
    for e in ents:
        W = lambda what, n=e.get('name', '?'): P(f'entry {n}: {what}')
        for k in ('name', 'made_for', 'kept', 'verified'):
            if blank(e.get(k)):
                W(f'missing {k}')
        if blank(e.get('weakness')) and not e.get('reference'):
            W('missing weakness (what the paper says it does badly); mark reference rows with reference: true')
        out.append(dict(e, note_links=note_links(e.get('note_labels'), labels, lang, W)))
    lin['entries'] = out
    for i, a in enumerate(lin.get('after') or []):
        for k in ('name', 'source', 'point'):
            if blank(a.get(k)):
                P(f'later development {i + 1}: missing {k} (auxiliary, with its primary source)')
    return lin


def load(spec_path):
    """Return (data for the page, problems)."""
    base = os.path.dirname(os.path.abspath(spec_path))
    spec = json.load(open(spec_path, encoding='utf-8'))
    probs = []
    P = lambda where, what: probs.append(f'{where}: {what}')
    rel = lambda p: os.path.join(base, p)
    lang = spec.get('lang', 'ja')

    # ---- introduction, map, sources
    bg = dict(spec.get('background') or {})
    for k in ('picture', 'summary', 'question', 'context', 'terms'):
        if blank(bg.get(k)):
            P('background', f'missing {k} (the shared introduction; picture = what is measured and what one wants to see; '
                            'summary = the paper\'s Summary and Introduction in plain words)')
    if bg.get('figure'):
        bg['figure'] = embed_crop(bg['figure'], rel, lambda what: P('background figure', what))
    pr = bg.get('primer')
    if blank(pr):
        P('background', "missing primer (how to read what the method outputs and the figures that follow; 'n/a: reason' when the paper has none)")
    elif not na(pr):
        for k in ('object', 'learn'):
            if blank(pr.get(k)):
                P('background primer', f'missing {k} (what the output is, in plain words; what one can learn from it)')
        if blank(pr.get('parts')) or any(blank(x.get('term')) or blank(x.get('meaning')) for x in pr.get('parts') or []):
            P('background primer', 'parts: the output taken apart (each term with its meaning)')
        if blank(pr.get('encodings')) or any(blank(x.get('mark')) or blank(x.get('meaning')) or blank(x.get('figures')) for x in pr.get('encodings') or []):
            P('background primer', 'encodings: every mark, size or colour the later figures use, with its meaning and the figures (ids) that use it')
    steps = spec.get('overview') or []
    if blank(steps):
        P('overview', 'no whole-method map (list every step, built or not)')
    for st in steps:
        for k in ('id', 'name', 'role', 'input', 'output'):
            if blank(st.get(k)):
                P(f"overview step {st.get('id', '?')}", f'missing {k}')
    step_ids = {st.get('id') for st in steps}
    # ---- storyline layer (optional, written before the units): the obstacles the paper names and the steps that answer them
    diffs = spec.get('difficulties')
    if diffs is not None:
        diff_ids = [d.get('id') for d in diffs]
        if blank(diffs):
            P('difficulties', 'empty (list the obstacles the paper names, or omit the layer)')
        if len(set(diff_ids)) != len(diff_ids):
            P('difficulties', 'ids must be unique')
        for d in diffs:
            for k in ('id', 'title', 'text'):
                if blank(d.get(k)):
                    P(f"difficulty {d.get('id', '?')}", f'missing {k} (text = why the obvious route or the earlier method fails, not only what is hard)')
        answered = set()
        for st in steps:
            if blank(st.get('why')):
                P(f"overview step {st.get('id', '?')}", 'missing why (why this step is needed here; the storyline layer is on)')
            ans = st.get('answers')
            if blank(ans):
                P(f"overview step {st.get('id', '?')}", "missing answers (ids of the difficulties it answers, or 'n/a: reason')")
            elif not na(ans):
                for x in ans:
                    if x not in diff_ids:
                        P(f"overview step {st.get('id', '?')}", f'answers {x!r}, which is not a difficulty id')
                    answered.add(x)
        for i in diff_ids:
            if i not in answered:
                P(f'difficulty {i}', 'no step answers it (an obstacle the method never meets, or a step is missing from the map)')
    labels = {}
    note = spec.get('note') or {}
    if note.get('aux'):
        if os.path.exists(rel(note['aux'])):
            labels = read_aux(rel(note['aux']))
        else:
            P('note', f"aux not found: {note['aux']}")
    methods = spec.get('methods') or {}
    impls = {'author': methods.get('author') or {}}
    for pr in methods.get('prior', []):
        impls[pr.get('id', '?')] = pr
    for iid, m in impls.items():
        for k in ('name', 'repo', 'url', 'commit', 'license', 'root'):
            if blank(m.get(k)):
                P(f'method {iid}', f'missing {k} (sources used: repository, URL, commit, licence)')
    code_map = check_code_map(spec.get('code_map'), impls, rel, step_ids, lambda what: P('code_map', what))
    lineage = check_lineage(spec.get('lineage'), labels, lang, lambda what: P('lineage', what))
    datasets = {d.get('id'): d for d in spec.get('datasets') or []}
    if blank(datasets):
        P('datasets', 'no datasets listed (sources used)')
    for did, d in datasets.items():
        for k in ('name', 'source', 'identity', 'level'):
            if blank(d.get(k)):
                P(f'dataset {did}', f'missing {k}')
        if d.get('level') == 'AI':
            for k in ('generator', 'truth'):
                if blank(d.get(k)):
                    P(f'dataset {did}', f'AI-created synthetic data needs {k} (script, and what the truth is)')
        elif d.get('level') not in LEVELS[:3]:
            P(f'dataset {did}', "level must be L1, L2 or L3 (data that was run), or 'AI' (synthetic demo data)")
    for i, u in enumerate(spec.get('unobtained') or []):
        for k in ('what', 'tried', 'instead'):
            if blank(u.get(k)):
                P(f'unobtained {i + 1}', f'missing {k} (what, places tried, what is used instead)')
    if 'requests' not in spec:
        P('requests', "missing request list (use [] when nothing is open)")
    for i, r in enumerate(spec.get('requests') or []):
        for k in ('what', 'where', 'serves', 'enables'):
            if blank(r.get(k)):
                P(f'request {i + 1}', f'missing {k}')

    # ---- step units (supplement)
    feats_out = []
    for f in spec.get('features', []):
        fid = f.get('id', '?')
        FP = lambda what, W=f'step unit {fid}': P(W, what)
        is_run = f.get('kind') == 'run'   # a run behind a results figure: no step-unit text, not listed in the supplement
        for k in (('title', 'limits') if is_run else ('title', 'background', 'question', 'idea', 'example', 'recap', 'limits')):
            if blank(f.get(k)):
                FP(f'missing {k}')
        if not is_run and f.get('step') not in step_ids:
            FP('step is not an id of the overview (where we are)')
        if f.get('dataset') not in datasets:
            FP('dataset is not an id of datasets (which data the run used)')
        fterms = f.get('terms') or []
        if blank(fterms) or any(blank(t.get('term')) or blank(t.get('meaning')) for t in fterms):
            FP('terms: every term needs term and meaning')
        fm = f.get('formula')
        if is_run:
            pass
        elif isinstance(fm, str):
            if not na(fm):
                FP("formula must be {text, source} or 'n/a: reason'")
        elif blank((fm or {}).get('text')) or blank((fm or {}).get('source')):
            FP('formula needs text and source')
        sp = f.get('selling_point') or {}
        if not is_run and (blank(sp.get('text')) or blank(sp.get('source'))):
            FP('selling point needs text and source')
        if not is_run and blank(f.get('note_labels')):
            FP('no note labels (where to read more)')
        nl = note_links(f.get('note_labels'), labels, lang, FP)
        rd = f.get('reading') or {}
        for k in (() if is_run else ('see', 'learn', 'trouble')):
            if blank(rd.get(k)):
                FP(f'reading lacks {k}')

        codes = {}
        for slot in ('author_code', 'prior_code'):
            c = f.get(slot)
            if isinstance(c, str):
                if not na(c):
                    FP(f"{slot} must be an excerpt or 'n/a: reason'")
                codes[slot] = {'na': c}
                continue
            if not c:
                FP(f"missing {slot} (use 'n/a: reason' when none applies)")
                continue
            impl = impls.get(c.get('impl', 'author' if slot == 'author_code' else ''))
            if not impl:
                FP(f'{slot}: unknown impl {c.get("impl")!r}')
                continue
            try:
                path, lines, text, sha = excerpt(rel(impl.get('root', '')), c)
            except (OSError, KeyError) as e:
                FP(f'{slot}: cannot read excerpt ({e})')
                continue
            for blk in c.get('roles', []) + [{'first': a, 'last': b, 'text': '-'} for a, b in c.get('fold', [])]:
                if not in_range([blk.get('first', 0), blk.get('last', 0)], c) or blank(blk.get('text')):
                    FP(f'{slot}: role/fold block {blk.get("first")}-{blk.get("last")} outside the excerpt or without text')
            params = c.get('params', [])
            check_params(params, slot, c, lines, fterms, FP)
            if slot == 'prior_code' and blank(c.get('failure')):
                FP('prior_code needs where the earlier method fails or differs on the same input')
            codes[slot] = {'impl': impl.get('name'), 'repo': impl.get('repo'), 'url': impl.get('url'),
                           'commit': impl.get('commit'), 'license': impl.get('license'), 'source': impl.get('source', ''),
                           'file': c['file'], 'first': c['first'], 'last': c['last'], 'text': text, 'sha256': sha,
                           'failure': c.get('failure', ''), 'roles': c.get('roles', []), 'fold': c.get('fold', []),
                           'link': bool(c.get('link')),
                           'params': [dict(p, grid_str=[vstr(v) for v in p['grid']], default_str=vstr(p['default']))
                                      for p in params]}
        ac, pc = codes.get('author_code') or {}, codes.get('prior_code') or {}
        check_presets(f.get('presets'), ac.get('params', []), 'preset', FP)
        if 'text' in pc:
            check_presets(f.get('prior_presets'), pc.get('params', []), 'earlier-method preset', FP)
            if pc.get('link') and len(pc.get('params', [])) != len(ac.get('params', [])):
                FP('prior_code link needs as many earlier-method parameters as authors\' ones')
            cmp = f.get('comparison') or []
            if blank(cmp):
                FP('no comparison list (pairs of line ranges: same / changed / author-only / prior-only)')
            for i, e in enumerate(cmp):
                rel_ = e.get('relation')
                if rel_ not in RELATIONS:
                    FP(f'comparison {i + 1}: relation must be one of {RELATIONS}')
                for k, why in (('does', 'what the code does, in plain words'), ('lineage', 'where it comes from: inherited from which work, changed, added, not used'),
                               ('text', 'what differs and what that changes in the output')):
                    if blank(e.get(k)):
                        FP(f'comparison {i + 1}: missing {k} ({why}); the relation label only summarises it')
                need_a, need_p = rel_ in ('same', 'changed', 'author-only'), rel_ in ('same', 'changed', 'prior-only')
                if need_a != (e.get('author') is not None) or need_p != (e.get('prior') is not None):
                    FP(f'comparison {i + 1}: ranges do not fit the relation {rel_!r}')
                if e.get('author') is not None and not in_range(e['author'], ac):
                    FP(f'comparison {i + 1}: author range {e.get("author")} outside the excerpt')
                if e.get('prior') is not None and not in_range(e['prior'], pc):
                    FP(f'comparison {i + 1}: earlier range {e.get("prior")} outside the excerpt')
            covered = [e['author'] for e in cmp if isinstance(e.get('author'), list)]
            for r in ac.get('roles', []):
                if not any(a <= r['last'] and r['first'] <= b for a, b in covered):
                    FP(f"comparison: authors' block L{r['first']}-{r['last']} has no pair or only-entry")

        results = {}
        rp = f.get('results')
        if blank(rp) or not os.path.exists(rel(rp)):
            FP(f'results file missing: {rp}')
        else:
            results = json.load(open(rel(rp), encoding='utf-8'))
            prov = results.get('provenance')
            if prov not in PROVENANCE:
                FP(f'results provenance must be one of {sorted(PROVENANCE)}')
            for k in ('script', 'commit', 'data'):
                if blank(results.get(k)):
                    FP(f'results lack {k}')
            rt = results.get('runtime_seconds')
            if not isinstance(rt, (int, float)):
                FP('results lack runtime_seconds (the time the longest run took)')
            if 'scale_down' not in results:
                FP("results lack scale_down (what is smaller than in the paper; use '' when nothing)")
            elif isinstance(rt, (int, float)) and rt > 300 and blank(results.get('over_budget')):
                FP(f'runtime {rt:.0f} s is over the 5-minute budget: say why in over_budget (e.g. kept because already finished)')
            if prov == 'AI re-implementation':
                par = results.get('parity') or {}
                if blank(par.get('against')) or par.get('max_abs_diff') is None or par.get('tolerance') is None \
                        or par['max_abs_diff'] > par['tolerance']:
                    FP('AI re-implementation without a passing parity record is not shown')
            for key in grid_keys(ac.get('params', []) if 'params' in ac else []):
                if key not in (results.get('author') or {}):
                    FP(f'author grid point {key!r} missing in results')
            for side, cc in (('author', ac), ('prior', pc)):
                for p in cc.get('params', []) if isinstance(cc, dict) else []:
                    k = (p.get('derives') or {}).get('key')
                    if k and any(k not in g for g in (results.get(side) or {}).values()):
                        FP(f"{side} param {p['name']}: derived key {k!r} missing in some {side} grid points")
            if 'text' in pc:
                for key in grid_keys(pc.get('params', [])):
                    if key not in (results.get('prior') or {}):
                        FP(f'earlier-method grid point {key!r} missing in results')

        check_run_card(f.get('run_card'), ac, pc, step_ids, FP)
        called, sell = check_called(f, impls, rel, FP)
        fig = embed_crop(f.get('figure') or {}, rel, FP)
        f = dict(f, run_role=check_role(f.get('run_role'), rel, FP))
        feats_out.append(dict(f, called=called, sell=sell, note_links=nl, codes=codes, results=results, figure=fig,
                              dataset_info=datasets.get(f.get('dataset'), {})))

    # ---- figure units (main line)
    feat_by_id = {f['id']: f for f in feats_out}
    figs_out = []
    n_main = (spec.get('paper') or {}).get('main_figures')
    figs = spec.get('figures') or []
    if not isinstance(n_main, int) or n_main < 1:
        P('paper', 'main_figures (the number of main-text figures) is required')
    else:
        nums = [g.get('number') for g in figs]
        if nums != list(range(1, n_main + 1)):
            P('figures', f'main-text figures must be listed once each, in order 1..{n_main} (found {nums})')
    for g in figs:
        GP = lambda what, W=f"figure {g.get('label', g.get('id', '?'))}": P(W, what)
        if g.get('pending'):
            # a figure unit not built yet (units are built one at a time); check_companion reports it as open
            for k in ('id', 'label', 'title'):
                if blank(g.get(k)):
                    GP(f'missing {k}')
            if (g.get('reproduction') or {}).get('level') not in LEVELS:
                GP('pending figure: give the reproduction level the readiness review (R32) found')
            figs_out.append(dict(g, note_links=note_links(g.get('note_labels'), labels, lang, GP)))
            continue
        for k in ('id', 'label', 'title', 'plain', 'trouble', 'handoff'):
            if blank(g.get(k)):
                GP(f'missing {k}')
        cl = g.get('claim') or {}
        if blank(cl.get('text')) or blank(cl.get('source')):
            GP('claim needs the main-text sentence or caption statement and its locator')
        reads = g.get('reads') or []
        if blank(reads) or any(blank(r.get('mark')) or blank(r.get('see')) or blank(r.get('learn')) for r in reads):
            GP('reads: every mark needs mark, see and learn (the paper figure is always explained)')
        for i, r_ in enumerate(reads):
            ck = r_.get('check')
            if blank(ck):
                GP(f"reads mark {r_.get('mark')}: needs a check (which preset to press and what to look at, or paper_only with the reason)")
            elif ck.get('paper_only'):
                if blank(ck.get('reason')):
                    GP(f"reads mark {r_.get('mark')}: paper_only needs the reason")
            else:
                if ck.get('step') not in feat_by_id:
                    GP(f"reads mark {r_.get('mark')}: check.step must be a step unit or demo id")
                else:
                    f_ = feat_by_id[ck['step']]
                    labels_ = [x.get('label') for x in (f_.get('presets') or []) + (f_.get('prior_presets') or [])]
                    if not any(isinstance(x, str) and x.startswith(ck.get('preset') or '\0') for x in labels_):
                        GP(f"reads mark {r_.get('mark')}: preset {ck.get('preset')!r} is not a preset of {ck['step']}")
                for k in ('look', 'result'):
                    if blank(ck.get(k)):
                        GP(f"reads mark {r_.get('mark')}: check lacks {k} (what to look at; what was observed)")
        if g.get('demo'):
            if g['demo'].get('step') not in feat_by_id or (feat_by_id[g['demo']['step']].get('run_role') or {}).get('role') != 'demo':
                GP("demo.step must be a run unit whose run_role is 'demo'")
            else:
                df = feat_by_id[g['demo']['step']]
                dps = ((df.get('codes') or {}).get('author_code') or {}).get('params') or []
                if not dps:
                    GP('the demo is the one run with controls: it needs at least one control')
                if blank(df.get('called')):
                    GP('the demo needs called: the whole code of the functions whose arguments are its controls (folded in the run), with sell ranges highlighted')
                elif blank(df.get('sell')):
                    GP('the demo needs sell: the ranges of the called code that are the selling points of the figure')
                if blank((df.get('run_role') or {}).get('values_note')):
                    GP('demo run_role needs values_note (how the call differs from the call behind the paper\'s figure, and why)')
                rs = feat_by_id.get((g.get('reproduction') or {}).get('step'))
                if rs and rs.get('kind') == 'run' and ((rs.get('codes') or {}).get('author_code') or {}).get('params'):
                    GP("a remake next to the demo must have no controls: one run with controls per figure (controls only on the demo)")
        elif (g.get('reproduction') or {}).get('level') != 'L4':
            GP('no demo: a figure with code needs a synthetic experiment to check the claims by hand (or level L4)')
        if (g.get('reproduction') or {}).get('level') != 'L4':
            dif = g.get('difference') or []
            if blank(dif):
                GP('no difference: say which steps and lines make the difference the figure shows (to the earlier method or between conditions)')
            for i, x in enumerate(dif):
                if blank(x.get('text')) or blank(x.get('where')):
                    GP(f'difference {i + 1}: needs text and where (file and lines)')
                if blank(x.get('steps')) or any(s_ not in step_ids for s_ in x.get('steps') or []):
                    GP(f'difference {i + 1}: steps must be ids of the whole-method map')
                if x.get('by') not in ('paper', 'note', 'speaker'):
                    GP(f"difference {i + 1}: by must be 'paper', 'note' or 'speaker' (whose statement it is)")
                check_where(x.get('where'), impls, rel, lambda what, i=i: GP(f'difference {i + 1}: {what}'))
        if g.get('talk') is not None:
            for k in ('takeaway', 'picture', 'property'):
                if blank((g.get('talk') or {}).get(k)):
                    GP(f'talk needs {k} (one sentence to take away; the picture to show; the one-word property of the method this figure shows)')
            if blank(((g.get('talk') or {}).get('panels') or {}).get('show')):
                GP('talk.panels.show: the panels to show (the rest, panels.rest, are said in a sentence or left to the appendix; the figure itself is never skipped)')
        pr_ = g.get('presenter') or {}
        for k in ('say', 'point', 'not_shown'):
            if blank(pr_.get(k)):
                GP(f'presenter notes lack {k}')
        for i, q in enumerate(pr_.get('questions') or []):
            if blank(q.get('q')) or blank(q.get('a')):
                GP(f'presenter question {i + 1}: needs q and a')
        rep = g.get('reproduction') or {}
        lv = rep.get('level')
        if lv not in LEVELS:
            GP('reproduction level must be L1–L4')
        elif lv == 'L4':
            if blank(rep.get('reason')):
                GP('L4 needs the reason (no code, or no runnable data yet) and what it links to')
        else:
            g = dict(g, reproduction=dict(rep, **check_role(rep, rel, GP)))
            if rep.get('step') not in feat_by_id:
                GP('reproduction step must be a step unit id (the run shown)')
            for x in rep.get('extra_steps') or []:
                if x.get('step') not in feat_by_id:
                    GP(f"extra run {x.get('step')!r} is not a step unit id")
                else:
                    x.update(check_role(x, rel, GP))
            for k in ('corresponds', 'not_transfer'):
                if blank(rep.get(k)):
                    GP(f'reproduction lacks {k} (which panel and claim the run corresponds to; what does not transfer)')
            if rep.get('step') in feat_by_id:
                dl = (feat_by_id[rep['step']].get('dataset_info') or {}).get('level')
                if dl and dl != lv:
                    GP(f'reproduction level {lv} differs from the level of the data used ({dl})')
        points = g.get('points') or []
        if blank(points) and lv != 'L4':
            GP('no figure selling point ↔ code selling point')
        for i, pt in enumerate(points):
            for k in ('panel', 'figure_point', 'code_point'):
                if blank(pt.get(k)):
                    GP(f'point {i + 1}: missing {k}')
            st = pt.get('step')
            if not (st in feat_by_id or na(st)):
                GP(f"point {i + 1}: step must be a step unit id or 'n/a: reason'")
            fc = pt.get('focus') or {}
            if st in feat_by_id:
                codes = feat_by_id[st]['codes']
                for side, slot in (('author', 'author_code'), ('prior', 'prior_code')):
                    if fc.get(side) is not None and not in_range(fc[side], codes.get(slot) or {}):
                        GP(f'point {i + 1}: focus {side} {fc[side]} outside the step unit\'s excerpt')
        for s in g.get('supplementary') or []:
            if blank(s.get('label')) or blank(s.get('cited_at')) or blank(s.get('why')):
                GP('supplementary figure needs label, cited_at (main-text locator) and why it is needed here')
            if s.get('figure'):
                s['figure'] = embed_crop(s['figure'], rel, GP)
        if blank(g.get('note_labels')):
            GP('no note labels (where to read more)')
        nl = note_links(g.get('note_labels'), labels, lang, GP)
        fig = embed_crop(g.get('figure') or {}, rel, GP)
        figs_out.append(dict(g, figure=fig, note_links=nl))
    used = {(g.get('demo') or {}).get('step') for g in figs} | {pt.get('step') for g in figs for pt in (g.get('points') or [])} | \
           {(g.get('reproduction') or {}).get('step') for g in figs} | \
           {x.get('step') for g in figs for x in ((g.get('reproduction') or {}).get('extra_steps') or [])}
    for f in feats_out:
        if f['id'] not in used:
            P(f"step unit {f['id']}", 'not linked from any figure (tie each step to the main text)')

    data = {k: spec.get(k) for k in ('title', 'lang', 'paper', 'claims', 'overview', 'requests', 'unobtained')}
    data['background'] = bg
    data['difficulties'] = diffs
    data['datasets'] = list(datasets.values())
    data['note'] = {'pdf': note.get('pdf', ''), 'deck_pdf': (spec.get('deck') or {}).get('pdf', '')}
    data['methods'] = {k: {kk: v.get(kk) for kk in ('name', 'repo', 'url', 'commit', 'license', 'source', 'files')}
                       for k, v in impls.items()}
    figure_ids = {g.get('id') for g in figs}
    for x in ((bg.get('primer') or {}).get('encodings') or []) if isinstance(bg.get('primer'), dict) else []:
        for fid in x.get('figures') or []:
            if fid not in figure_ids:
                P('background primer', f'encoding {x.get("mark")!r} cites figure {fid!r}, which is not a figure id')
    data['code_map'] = code_map
    data['lineage'] = lineage
    data['figures'] = figs_out
    data['features'] = feats_out
    return data, probs
