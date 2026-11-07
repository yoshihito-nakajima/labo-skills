#!/usr/bin/env python3
"""Check the intake record of a reading note (literature-intake.md) and print the proposal table.

  check_intake.py INTAKE.json [--table] [--allow-open]

Exit 1 on an inconsistent record, or on open `must` entries unless --allow-open.
"""
import argparse, json, sys

KINDS = {'reference', 'supplement', 'code', 'data', 'figure'}
NEEDS = {'must', 'useful', 'optional'}
ACCESS = {'open', 'publisher-login', 'paywalled', 'unsafe', 'unknown'}
STATUS = {'obtained', 'read', 'needs-user', 'alternate-proposed', 'alternate-confirmed', 'avoided', 'unobtained'}
HAVE = {'obtained', 'read'}


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip()) or v == [] or v == {}


def check(data):
    probs, open_ = [], []
    ents = data.get('entries') or []
    ids = {e.get('id') for e in ents}
    if len(ids) != len(ents):
        probs.append(('intake', 'duplicate or missing entry ids'))
    for e in ents:
        w = f"entry {e.get('id', '?')}"
        for k in ('id', 'work', 'why'):
            if blank(e.get(k)):
                probs.append((w, f'missing {k}'))
        for k, allowed in (('kind', KINDS), ('need', NEEDS), ('access', ACCESS), ('status', STATUS)):
            if e.get(k) not in allowed:
                probs.append((w, f'{k} must be one of {sorted(allowed)}'))
        d = e.get('depth')
        if not isinstance(d, int) or d < 0:
            probs.append((w, 'depth must be an integer (0: the paper and its supplement)'))
        elif d > 0 and e.get('led_by') not in ids | {'paper'}:
            probs.append((w, 'depth > 0 needs led_by (the entry or the paper that led to this work)'))
        if e.get('kind') == 'figure' and e.get('status') in HAVE:
            lic = e.get('licence')
            if blank(lic) or blank(e.get('credit')) or e.get('changes') is None:
                probs.append((w, 'a picture from outside the source needs licence, credit and changes (what was altered, or "none")'))
            if e.get('ai_made') and not (e.get('user_permission') and e.get('user_permission_on')):
                probs.append((w, "an AI-made picture needs the user's permission for that picture (user_permission, user_permission_on)"))
        st = e.get('status')
        if st in HAVE:
            if blank(e.get('stored_at')) or blank((e.get('identity') or {}).get('sha256')) or blank((e.get('identity') or {}).get('retrieved')):
                probs.append((w, 'obtained/read needs stored_at and identity (sha256, retrieved)'))
            if e.get('access') != 'open' and not e.get('user_supplied'):
                probs.append((w, 'a non-open source is used without the user having supplied it (avoid it, or ask)'))
        else:
            if st != 'alternate-confirmed' and blank(e.get('tried')) and e.get('access') == 'open':
                probs.append((w, 'not obtained: record the places tried'))
            if st == 'needs-user' and (blank(e.get('unlocks')) or blank(e.get('where_likely'))):
                probs.append((w, 'needs-user: say what it unlocks (unlocks) and where it is probably available (where_likely)'))
            if st == 'avoided' and blank(e.get('avoided_because')):
                probs.append((w, 'avoided: give avoided_because'))
            if e.get('need') == 'must' and st != 'alternate-confirmed':
                open_.append((w, f'must item is {st}'))
        a = e.get('alternate') or {}
        if st in ('alternate-proposed', 'alternate-confirmed'):
            if blank(a.get('what')) or blank(a.get('why')):
                probs.append((w, 'substitute needs what and why'))
            if a.get('free') is not True:
                probs.append((w, 'a substitute must be free and open (free: true)'))
        if st == 'alternate-confirmed' and (a.get('confirmed_by_user') is not True or blank(a.get('confirmed_on'))):
            probs.append((w, 'a substitute is used only after the user confirmed it (confirmed_by_user, confirmed_on)'))
    return probs, open_


def table(data):
    ents = data.get('entries') or []
    groups = [('Obtained', lambda e: e.get('status') in HAVE), ('Asked of the user', lambda e: e.get('status') in ('needs-user', 'unobtained', 'avoided')),
              ('Substitutes for confirmation / confirmed', lambda e: str(e.get('status', '')).startswith('alternate'))]
    out = []
    for title, f in groups:
        rows = [e for e in ents if f(e)]
        out.append(f'### {title} ({len(rows)})')
        if not rows:
            out.append('(none)\n'); continue
        out.append('| id | work | need | relation | why / what it unlocks | where / how |')
        out.append('|---|---|---|---|---|---|')
        for e in rows:
            a = e.get('alternate') or {}
            how = (f"substitute: {a.get('what')} ({a.get('why')})" if a else (e.get('where_likely') or e.get('avoided_because') or e.get('stored_at') or ''))
            out.append(f"| {e.get('id')} | {e.get('work')} | {e.get('need')} | {e.get('relation', '')} | {e.get('why')}{' → ' + e['unlocks'] if e.get('unlocks') else ''} | {how} |")
        out.append('')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path'); ap.add_argument('--table', action='store_true'); ap.add_argument('--allow-open', action='store_true')
    a = ap.parse_args()
    data = json.load(open(a.path, encoding='utf-8'))
    probs, open_ = check(data)
    if a.table:
        print(table(data))
    for w, p in probs:
        print(f'{w}: {p}')
    for w, p in open_:
        print(f'{w}: OPEN ({p})')
    print(f'{len(probs)} problem(s), {len(open_)} open')
    sys.exit(1 if probs or (open_ and not a.allow_open) else 0)


if __name__ == '__main__':
    main()
