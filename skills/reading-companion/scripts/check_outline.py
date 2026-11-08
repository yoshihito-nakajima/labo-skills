#!/usr/bin/env python3
"""Check the storyline layer of a companion spec before any unit is written.

  check_outline.py companion.json

Looks only at the parts that fix the story: the shared introduction (background), the method map
(overview), and the optional difficulties with the steps that answer them. Units, figures and
code are not required yet. Exit 1 on problems.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from companion_lib import load  # noqa: E402

SCOPE = ('background', 'overview', 'difficult', 'difficulty')


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    _, probs = load(sys.argv[1])
    mine = [p for p in probs if p.startswith(SCOPE)]
    print('\n'.join(mine) if mine else 'ok')
    print(f'{len(mine)} problem(s) in the storyline layer ({len(probs) - len(mine)} elsewhere, not checked yet)')
    sys.exit(1 if mine else 0)


if __name__ == '__main__':
    main()
