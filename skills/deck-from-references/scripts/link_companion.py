#!/usr/bin/env python3
"""Link slides to the companion page (companion.json) they come from, and main pages to appendix pages.

  link_companion.py list  --companion companion.json
  link_companion.py check BODY.tex [--appendix APP.tex] --companion companion.json [--allow-appendix-figures]

Unit ids: intro, summary, lineage, lineage:<entry name>, codemap, params, after, figN and figN:<claim|reading|difference|run|check|presenter>,
step:<id>, run:<id>. A frame (title frames [plain] are skipped) needs \\fromunit{ids} or \\nounit{reason}.
check reports: a frame with neither; an id that is not a unit of the companion; main-text figures that the body does not
explain (unless they are in the appendix and --allow-appendix-figures); figure pages out of order in the body
(Fig.1 .. Fig.N must appear in ascending order, by each page's first unit; later units are sources only; a figure shown only as an example, \\asexample{...} with \\exampletag, is outside the order); \\appref{X} without a matching \\applabel{X} in the appendix; a page that shows a figure without \\colorkey or \\nocolorkey{reason}.
Exit status 1 on a problem.
"""
import argparse, json, re, sys

PARTS = {'claim', 'reading', 'difference', 'run', 'check', 'presenter'}


def units(spec):
    u = {'intro', 'summary', 'lineage', 'codemap', 'params', 'after', 'sources', 'checks', 'limits', 'primer'}   # checks: every figure's 'check'; limits: what the page does not show
    for e in (spec.get('lineage') or {}).get('entries', []):
        u.add('lineage:' + e['name'])
    for g in spec.get('figures', []):
        u.add(g['id'])
    for f in spec.get('features', []):
        u.add(('run:' if f.get('kind') == 'run' else 'step:') + f['id'])
    return u


def frames(text):
    out = []
    for m in re.finditer(r'\\begin\{frame\}(\[[^\]]*\])?(.*?)\\end\{frame\}', text, re.S):
        if 'plain' in (m.group(1) or ''):
            continue
        t = re.search(r'\\frametitle\{([^}]*)\}', m.group(2))
        out.append(((t.group(1) if t else '?')[:40], m.group(2)))
    return out


def ids_in(body):
    ks = []
    for m in re.finditer(r'\\fromunit\{([^}]*)\}', body):
        ks += [k.strip() for k in m.group(1).split(',') if k.strip()]
    return ks


def examples_in(body):
    ks = []
    for m in re.finditer(r'\\asexample\{([^}]*)\}', body):
        ks += [k.strip() for k in m.group(1).split(',') if k.strip()]
    return ks


def check(body_tex, app_tex, spec, allow_app_figs):
    probs, U = [], units(spec)
    figs = {g['id']: g.get('number') for g in spec.get('figures', []) if not g.get('pending')}
    seen_order, covered = [], set()
    for title, body in frames(body_tex):
        ids = ids_in(body)
        if not ids and '\\nounit' not in body:
            probs.append(f'body page "{title}": neither \\fromunit nor \\nounit')
        for k, i in enumerate(ids):
            base, _, part = i.partition(':') if i.startswith('fig') else (i, '', '')
            if i.startswith('fig'):
                if base not in U or (part and part not in PARTS):
                    probs.append(f'body page "{title}": unknown unit {i}')
                elif base in figs and k == 0:   # the page's first unit says what it explains; other units are only sources
                    covered.add(base); seen_order.append((figs[base], title))
            elif i not in U:
                probs.append(f'body page "{title}": unknown unit {i}')
        for ex in examples_in(body):
            base = ex.split(':')[0]
            if base not in U:
                probs.append(f'body page "{title}": \\asexample names an unknown unit {ex}')
        if examples_in(body) and '\\exampletag' not in body:
            probs.append(f'body page "{title}": a figure shown as an example must be marked with \\exampletag')
        for a in re.findall(r'\\appref\{([^}]*)\}', body):
            if f'\\applabel{{{a}}}' not in (app_tex or ''):
                probs.append(f'body page "{title}": \\appref{{{a}}} has no \\applabel in the appendix')
    nums = [n for n, _ in seen_order]
    for (n1, t1), (n2, t2) in zip(seen_order, seen_order[1:]):
        if n2 < n1:
            probs.append(f'figure pages out of order: Fig.{n2} ("{t2}") comes after Fig.{n1} ("{t1}"); keep Fig.1 .. Fig.N ascending')
            break
    for title, body in frames(body_tex) + frames(app_tex or ''):
        if re.search(r'\\includegraphics|\\picH|\\pic\b|\\figcard', body) and '\\colorkey' not in body and '\\nocolorkey' not in body:
            probs.append(f'page "{title}": shows a figure without \\colorkey (what its colour or size means) or \\nocolorkey{{reason}}')
    app_cov = set()
    for title, body in frames(app_tex or ''):
        ids = ids_in(body)
        if not ids and '\\nounit' not in body:
            probs.append(f'appendix page "{title}": neither \\fromunit nor \\nounit')
        for i in ids:
            base = i.split(':')[0] if i.startswith('fig') else i
            if base not in U and i not in U:
                probs.append(f'appendix page "{title}": unknown unit {i}')
            app_cov.add(base)
    for fid, n in figs.items():
        if fid not in covered and not (allow_app_figs and fid in app_cov):
            probs.append(f'Fig.{n}: no page in the body explains it (the main-text figures are explained in order)')
    return probs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['list', 'check']); ap.add_argument('body', nargs='?')
    ap.add_argument('--appendix'); ap.add_argument('--companion', required=True); ap.add_argument('--allow-appendix-figures', action='store_true')
    a = ap.parse_args(); spec = json.load(open(a.companion, encoding='utf-8'))
    if a.cmd == 'list':
        print('\n'.join(sorted(units(spec)))); return
    probs = check(open(a.body, encoding='utf-8').read(), open(a.appendix, encoding='utf-8').read() if a.appendix else '', spec, a.allow_appendix_figures)
    print('\n'.join(probs)); print(f'{len(probs)} problem(s)'); sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
