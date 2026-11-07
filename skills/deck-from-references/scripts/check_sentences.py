#!/usr/bin/env python3
"""Report slide lines that are not short full sentences: the top line (\\frametitle), the bottom line and the next question (\\closing).

  check_sentences.py page.tex [page2.tex ...] [--max-title 26] [--max-bottom 32]

A line carries a subject particle (は が も) and stays short; Japanese lines end without 。, English lines with a full stop,
questions with a question mark. Reports only (exit 0);
the heuristic misses and over-reports, so a person decides. Japanese; Latin lines are checked for an ending stop only.
"""
import re, sys, argparse


def plain(t):
    t = re.sub(r"\\(ph|kwr|kwn|kwo|textbf|emph|href)\{([^{}]*)\}(\{[^{}]*\})?", lambda m: m.group(3)[1:-1] if m.group(1) == 'href' and m.group(3) else m.group(2), t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", "", t)
    return re.sub(r"[{}$\\~ ]", "", t).strip()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--max-title', type=int, default=26); ap.add_argument('--max-bottom', type=int, default=32)
    a = ap.parse_args(); n = 0
    for f in a.files:
        s = open(f, encoding='utf-8').read()
        for fr in re.finditer(r"\\begin\{frame\}(\[[^\]]*\])?(.*?)\\end\{frame\}", s, re.S):
            if 'plain' in (fr.group(1) or ''):
                continue
            body = fr.group(2)
            lines = []
            m = re.search(r"\\frametitle\{((?:[^{}]|\{[^{}]*\})*)\}", body)
            if m: lines.append(('top', plain(m.group(1)), a.max_title))
            m = re.search(r"\\closing(?:\[((?:[^\]])*)\])?\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", body)
            if m:
                lines.append(('bottom', plain(m.group(2)), a.max_bottom))
                if m.group(1): lines.append(('question', plain(m.group(1)), a.max_bottom))
            for role, t, lim in lines:
                probs = []
                ja = bool(re.search(r"[ぁ-んァ-ヶ一-龥]", t))
                if role == 'question' and not re.search(r"[？?]$", t): probs.append('a question ends with a question mark')
                elif role != 'question' and ja and t.endswith('。'): probs.append('Japanese lines carry no full stop')
                elif role != 'question' and not ja and not t.endswith('.'): probs.append('an English line ends with a full stop')
                if re.search(r"[ぁ-んァ-ヶ一-龥]", t) and not re.search(r"[はがも]", t): probs.append('no subject particle (は が も): subject missing?')
                if len(t) > lim: probs.append(f'{len(t)} characters, longer than {lim}')
                if probs:
                    n += 1; print(f"{f}: {role} line \"{t}\": " + '; '.join(probs))
    print(f"{n} line(s) reported")
    return 0


if __name__ == '__main__':
    sys.exit(main())
