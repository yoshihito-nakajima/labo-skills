#!/usr/bin/env python3
"""Completion gate for reading notes: resources, lineage, unit chain, claim gloss.

  check_coverage.py COVERAGE.json [--json] [--allow-open] [--max-plain 0.7]

Data file (all sections optional; see resource-ledger.md, lineage-and-comparison.md,
unit-chain-and-claim-gloss.md):

  {"resources":   [{"id","kind","what","status","locator","read_in","must_read",
                    "tried":[...],"request","free_alternatives":[...],
                    "stand_in":{"label","note","permission"}}],
   "comparisons": [{"id","relation","claim_loc","unit","primary":{"work","locator","status"},
                    "purpose","place","inherited","changed","weakness","verified",
                    "excerpt","translation_needed","translation","code"}],
   "overview":    {"lineage_label","values_label",
                    "code_notes":[{"unit","blocks":[{"lines","does","source","difference"}]}],
                    "differences":[{"figure","steps":[...],"where","by"}]},
   "units":       [{"id","parent","needs":[...],"produces":[...],"bridge_in"}],
   "sentences":   [{"unit","n","kind","gloss":{"object","known","claim","benefit","added"}}]}

Exit status 1 when a record is missing or inconsistent, or when entries are open
(unobtained, unread, stand-in only) and --allow-open is not given. A passing run shows the
records are complete; it does not show that the text is faithful or understandable.
"""
import argparse, json, sys

RES_STATUS = {'listed', 'obtained', 'read', 'unobtained'}
MUST_KINDS = {'code', 'procedure', 'claim-figure', 'derivation', 'data', 'methods', 'validation'}
RELATIONS = {'inherited', 'baseline', 'criticised', 'encompassing', 'encompassed', 'origin', 'prior-version'}
TREATED = RELATIONS - {'origin'}
CMP_STATUS = {'read', 'unread', 'unobtained'}
GLOSS_KINDS = {'cite', 'property', 'show'}
KINDS = GLOSS_KINDS | {'plain'}


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip()) or v == [] or v == {}


def check(data, max_plain):
    problems, open_ = [], []
    ids = set()
    for r in data.get('resources', []):
        rid = r.get('id', '?')
        if rid in ids:
            problems.append((f'resource {rid}', 'duplicate id'))
        ids.add(rid)
        st = r.get('status')
        if st not in RES_STATUS:
            problems.append((f'resource {rid}', 'missing or unknown status'))
            continue
        # an explicit must_read: false overrides the default of the kind, and needs the reason it is not needed
        must = r['must_read'] if 'must_read' in r else r.get('kind') in MUST_KINDS
        if r.get('must_read') is False and r.get('kind') in MUST_KINDS and blank(r.get('reason')):
            problems.append((f'resource {r.get("id", "?")}', 'must_read: false for an item of a must-read kind needs a reason'))
        if st == 'unobtained':
            if blank(r.get('tried')):
                problems.append((f'resource {rid}', 'unobtained without places tried'))
            if blank(r.get('request')):
                problems.append((f'resource {rid}', 'unobtained without the stated request (what is wanted and why)'))
            si = r.get('stand_in')
            if si is not None and str(si.get('label', '')).strip() not in ('AI-created', 'AI 作成', 'AI作成'):
                problems.append((f'resource {rid}', 'stand-in is not labelled AI-created'))
            if si is not None and blank(si.get('permission')):
                problems.append((f'resource {rid}', 'stand-in without the user\'s recorded per-resource permission (who, when, wording)'))
            open_.append((f'resource {rid}', 'stand-in only' if si else 'unobtained'))
        elif must and st != 'read':
            problems.append((f'resource {rid}', f'must-read item is only {st}'))
        elif st == 'read' and blank(r.get('read_in')):
            problems.append((f'resource {rid}', 'read but no unit uses it (read_in)'))
        elif st == 'listed' and not must and blank(r.get('reason')):
            problems.append((f'resource {rid}', 'listed-only item without a reason it was not read'))
    for c in data.get('comparisons', []):
        cid = c.get('id', '?')
        rel = c.get('relation')
        if rel not in RELATIONS:
            problems.append((f'comparison {cid}', 'missing or unknown relation'))
            continue
        prim = c.get('primary') or {}
        for k in ('work', 'locator'):
            if blank(prim.get(k)) and prim.get('status') != 'unobtained':
                problems.append((f'comparison {cid}', f'primary has no {k}'))
        st = prim.get('status')
        if st not in CMP_STATUS:
            problems.append((f'comparison {cid}', 'primary status missing or unknown'))
        elif st != 'read':
            open_.append((f'comparison {cid}', f'primary {st}'))
        for k in (('purpose', 'place') if rel == 'origin' else ('purpose', 'place', 'inherited', 'changed')):
            if blank(c.get(k)):
                problems.append((f'comparison {cid}', f'missing {k}'))
        if blank(c.get('claim_loc')):
            problems.append((f'comparison {cid}', 'missing claim_loc (where the paper says it)'))
        if rel in TREATED:
            for k in ('weakness', 'verified'):   # the overview table's columns (lineage-and-comparison.md#overview-table)
                if blank(c.get(k)):
                    problems.append((f'comparison {cid}', f"missing {k} for the lineage overview ('n/a: reason' when none)"))
        if rel in TREATED and st == 'read':
            if not c.get('excerpt'):
                problems.append((f'comparison {cid}', 'treated relation without displayed excerpt'))
            if c.get('translation_needed') and not c.get('translation'):
                problems.append((f'comparison {cid}', 'translation required but not recorded'))
            code = c.get('code')
            if blank(code):
                problems.append((f'comparison {cid}', "code comparison not recorded (use 'diff', 'executed' or 'n/a: reason')"))
            elif str(code).startswith('n/a') and ':' not in str(code):
                problems.append((f'comparison {cid}', "n/a code entry needs a reason ('n/a: reason')"))
    ov = data.get('overview')
    if ov is None:
        open_.append(('overview', 'no overview record (lineage table, values table, code-block notes, figure differences)'))
    else:
        for k in ('lineage_label', 'values_label'):
            if blank(ov.get(k)):
                problems.append(('overview', f'missing {k} (the label of the lineage table / the values table in the note)'))
        for n in ov.get('code_notes', []):
            for i, b_ in enumerate(n.get('blocks', [])):
                for k in ('lines', 'does', 'source', 'difference'):
                    if blank(b_.get(k)):
                        problems.append((f"code notes {n.get('unit', '?')} block {i + 1}", f'missing {k} (what it does in words; where it comes from; what differs and what that changes)'))
        if blank(ov.get('code_notes')):
            problems.append(('overview', 'no code_notes (notes under each author-code excerpt)'))
        if blank(ov.get('differences')):
            problems.append(('overview', 'no differences (per main-text figure: which steps and lines make its difference)'))
        for i, d_ in enumerate(ov.get('differences', [])):
            if blank(d_.get('figure')) or blank(d_.get('steps')) or blank(d_.get('where')) or d_.get('by') not in ('paper', 'note', 'speaker'):
                problems.append((f'difference {i + 1}', "needs figure, steps, where and by ('paper', 'note' or 'speaker')"))
    units = data.get('units', [])
    produced, seen = set(), set()
    for u in units:
        uid = u.get('id', '?')
        if uid in seen:
            problems.append((f'unit {uid}', 'duplicate id'))
        par = u.get('parent')
        if par and par not in seen and par != 'root':
            problems.append((f'unit {uid}', f'parent {par} unknown or later'))
        bridge = str(u.get('bridge_in') or '')
        if blank(bridge):
            problems.append((f'unit {uid}', 'missing bridge_in (opening)'))
        for need in u.get('needs', []):
            key = need[len('external:'):] if need.startswith('external:') else need
            if not need.startswith('external:') and need not in produced:
                problems.append((f'unit {uid}', f'need {need!r} is not produced by an earlier unit (mark external: if from outside)'))
            if key and key not in bridge:
                problems.append((f'unit {uid}', f'opening does not name need {key!r}'))
        produced |= set(u.get('produces', []))
        seen.add(uid)
    consumed = {n for u in units for n in u.get('needs', [])}
    for u in units:
        if u.get('produces') and not (set(u['produces']) & consumed) and not u.get('terminal'):
            problems.append((f"unit {u.get('id', '?')}", "produces nothing any later unit needs (set terminal: true if it ends a line)"))
    per_unit = {}
    for s in data.get('sentences', []):
        label = f"sentence {s.get('unit', '?')}#{s.get('n', '?')}"
        k = s.get('kind')
        if k not in KINDS:
            problems.append((label, 'missing or unknown kind'))
            continue
        per_unit.setdefault(s.get('unit', '?'), []).append(k)
        if k in GLOSS_KINDS:
            g = s.get('gloss') or {}
            need = ['object', 'known', 'claim', 'benefit'] + (['added'] if k == 'cite' else [])
            for part in need:
                if blank(g.get(part)):
                    problems.append((label, f'{k} sentence lacks gloss part {part}'))
    for uid, ks in per_unit.items():
        share = ks.count('plain') / len(ks)
        if len(ks) >= 5 and share > max_plain:
            problems.append((f'unit {uid}', f'{share:.0%} of sentences marked plain; classification looks skipped'))
    return problems, open_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--allow-open', action='store_true')
    ap.add_argument('--max-plain', type=float, default=0.7)
    a = ap.parse_args()
    data = json.load(open(a.path))
    problems, open_ = check(data, a.max_plain)
    if a.json:
        print(json.dumps([{'where': w, 'problem': p, 'kind': 'record'} for w, p in problems] +
                         [{'where': w, 'problem': p, 'kind': 'open'} for w, p in open_], ensure_ascii=False, indent=1))
    else:
        for w, p in problems:
            print(f'{w}: {p}')
        for w, p in open_:
            print(f'{w}: OPEN ({p})')
    bad = bool(problems) or (bool(open_) and not a.allow_open)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
