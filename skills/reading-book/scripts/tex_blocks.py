#!/usr/bin/env python3
"""Cut TeX into labelled statement blocks: a statement environment plus the proof that follows it.

Shared by make_packet.py (which records the blocks a packet targets) and review_coverage.py (which
matches reviewed blocks against the current canonical text), so both use one rule:

- a block starts at ``\\begin{ENV}`` for a statement environment and ends at its ``\\end{ENV}``;
- its key is the first ``\\label`` inside that environment (unlabelled blocks are counted, not keyed);
- if the next non-blank, non-comment line opens ``\\begin{proof}``, the block extends to the matching
  ``\\end{proof}`` (nested proofs are balanced); up to eight lines that hold only an index or
  navigation macro (``\\index{...}`` and the like) may stand in between;
- the hash ignores blank lines, comment-only lines, lines holding only an index or navigation macro,
  and runs of white space, so re-wrapping or re-indexing does not count as a mathematical change;
- ``strip_line_numbers`` removes the ``123: `` prefixes some packets put on every copied line.

A block whose environment or proof is cut off by the end of the text is marked ``complete: False``.
"""
from __future__ import annotations

import hashlib
import re

RESULT_ENVS = ("theorem", "lemma", "proposition", "corollary")
STATEMENT_ENVS = RESULT_ENVS + ("definition", "axiom")
BEGIN = re.compile(r"\\begin\{(%s)\*?\}" % "|".join(STATEMENT_ENVS))
LABEL = re.compile(r"\\label\{([^}]+)\}")
SECTION = re.compile(r"\\(chapter|section|subsection)\*?(?:\[[^\]]*\])?\{")
PROOF_BEGIN = re.compile(r"\\begin\{proof\}")
PROOF_END = re.compile(r"\\end\{proof\}")
# Index/navigation macros that sit alone on a line between a statement and its proof
# (e.g. \index{...}, \termat{...}{...}{...}); prose lines and environments end the search.
GAP_MACRO = re.compile(r"\\(?!begin\b|end\b|chapter\b|section\b|subsection\b|paragraph\b)[A-Za-z]+\*?(?:\[[^\]]*\])?\{")
MAX_GAP_MACROS = 8


def _norm(lines: list[str]) -> list[str]:
    out = []
    for x in lines:
        s = x.strip()
        if not s or s.startswith("%") or (GAP_MACRO.match(s) and s.endswith("}")):
            continue
        out.append(" ".join(s.split()))
    return out


def digest(lines: list[str]) -> str:
    # one string with single spaces, so where lines are broken does not matter
    return hashlib.sha256(" ".join(_norm(lines)).encode()).hexdigest()


NUMBERED = re.compile(r"^\s*\d+: ?")


def strip_line_numbers(text: str) -> str:
    """Drop ``123: `` prefixes when most non-blank lines carry them (numbered packet copies)."""
    lines = text.splitlines()
    body = [x for x in lines if x.strip()]
    if body and sum(bool(NUMBERED.match(x)) for x in body) >= 0.8 * len(body):
        return "\n".join(NUMBERED.sub("", x, count=1) for x in lines)
    return text


def blocks(text: str) -> list[dict]:
    """Return the statement blocks of ``text`` in order.

    Each block: ``label`` (or None), ``env``, ``start``/``end`` (1-based, inclusive), ``stmt_end``,
    ``has_proof``, ``complete``, ``hash`` (statement and proof), ``stmt_hash`` and ``section``
    (label or title of the enclosing chapter/section/subsection).
    """
    lines = text.splitlines()
    out: list[dict] = []
    section = ""
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if SECTION.search(line):
            lab = LABEL.search(line) or (LABEL.search(lines[i + 1]) if i + 1 < n else None)
            section = lab.group(1) if lab else line.strip()[:80]
        m = BEGIN.search(line)
        if not m or line.lstrip().startswith("%"):
            i += 1
            continue
        env = m.group(1)
        end_env = re.compile(r"\\end\{%s\*?\}" % env)
        j, complete = i, False
        while j < n:
            if end_env.search(lines[j]) and (j > i or end_env.search(line[m.end():])):
                complete = True
                break
            j += 1
        stmt_end = min(j, n - 1)
        label = None
        for k in range(i, stmt_end + 1):
            lab = LABEL.search(lines[k])
            if lab:
                label = lab.group(1)
                break
        end, has_proof = stmt_end, False
        k, macros = stmt_end + 1, 0
        while k < n:
            s = lines[k].strip()
            if not s or s.startswith("%"):
                k += 1
            elif macros < MAX_GAP_MACROS and GAP_MACRO.match(s) and s.endswith("}"):
                k, macros = k + 1, macros + 1
            else:
                break
        if complete and k < n and PROOF_BEGIN.search(lines[k]):
            has_proof, depth, p = True, 0, k
            proof_complete = False
            while p < n:
                depth += len(PROOF_BEGIN.findall(lines[p])) - len(PROOF_END.findall(lines[p]))
                if depth <= 0:
                    proof_complete = True
                    break
                p += 1
            end = min(p, n - 1)
            complete = proof_complete
        out.append({
            "label": label, "env": env, "start": i + 1, "stmt_end": stmt_end + 1, "end": end + 1,
            "has_proof": has_proof, "complete": complete, "section": section,
            "hash": digest(lines[i:end + 1]), "stmt_hash": digest(lines[i:stmt_end + 1]),
        })
        i = end + 1
    return out


def keyed(text: str) -> dict[str, dict]:
    """Labelled blocks by label (first occurrence wins)."""
    res: dict[str, dict] = {}
    for b in blocks(text):
        if b["label"] and b["label"] not in res:
            res[b["label"]] = b
    return res
