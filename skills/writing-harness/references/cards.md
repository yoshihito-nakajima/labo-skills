# Cards, status, fingerprints and structure

A harness directory holds the facts of one paper as small cards. The author
writes the prose; the agent keeps the facts. Git history is the version record.

```
<harness>/
    harness.toml        settings (language, paths, preamble)
    story.md            the author's story ledger
    vocab.toml          names of notions and whether they are decided
    style.toml          style rules for this paper only
    structure.yaml      reading order: sections and the cards they show
    cards/def/*.md      definition cards
    cards/prop/*.md     theorem, proposition, lemma and corollary cards
    cards/expl/*.md     the author's prose (explanation cards)
    reviews/<date>/     frozen copies and triage of each review round
    paper/              rendered TeX (generated)
```

## Who edits what

| Layer | Files | Author | Agent |
|---|---|---|---|
| Facts | `cards/def`, `cards/prop` | reviews, asks for changes | writes statements and gap-free proofs, verifies, links Lean |
| Vocabulary | `vocab.toml` | decides names | proposes names, checks generality and granularity |
| Structure | `structure.yaml` | decides order, sections, what is shown | checks dependencies, forward references, unused cards |
| Prose | `cards/expl` | writes everything in the body | proposes drafts only when asked; comments in `reviews/` |

## Fact cards

Markdown with YAML front matter and fixed `## ` sections. TeX is written as in
the paper.

```
---
id: def-graded-set           # stable kebab-case id; never reused for another fact
kind: definition             # definition | theorem | proposition | lemma | corollary
label: def:graded-set        # TeX label (default card:<id>)
title: Graded set
symbols: ['G']               # notation introduced here (vocab.toml keys)
requires: []                 # hard prerequisites (card ids)
status: drafted              # status ladder below
lean: []                     # Lean declarations that formalize this card
source: ''                   # where the fact came from (citation, note, earlier draft)
questions: []                # open questions for the author
---
## Statement
## Proof          (not for definitions)
## Shortcuts      (alternative routes found while proving or formalizing)
## Notes          (generality, alternatives, names in the literature)
```

The proof is a **reference proof**: numbered steps `(1) ...`, `(2) ...`, each
ending with its justification, with no gap. It is the paper's proof only when
the author chooses it in `structure.yaml`; otherwise the author's own proof
(an explanation card with `role: proof`) is printed. Keep the map from the
author's sentences to these steps (`covers` / `omits`) so any omitted step can
be produced on request.

## Explanation cards

```
---
id: x-why-grade
kind: explanation
role: motivation             # motivation | proof | remark | transition | intro
explains: [thm-grading]      # fact cards this text talks about
anchors: {thm-grading: 3f2a9c1e}   # fingerprints when the text was last read
covers: {thm-grading: [1, 2]}      # reference-proof steps written out
omits:  {thm-grading: [3]}         # steps deliberately skipped
---
<the author's TeX>
```

`role: proof` with `explains: [X]` makes the card the paper's proof of `X`.

## Status ladder

`stated` -> `drafted` (a proof exists) -> `gap-free` (every step justified) ->
`verified` (an independent check is recorded in `reviews/`) -> `lean`
(formalized). A card moves down when its statement changes. The ladder records
work done; it does not certify truth by itself.

`lean` requires the `lean:` list, and only for a formalization of the card's
own objects and statement. An abstract skeleton (the same proof shape over
placeholder structures) is recorded in `Notes` or `Shortcuts`, never as `lean`.
Name exactly what the Lean declaration checks when it differs from the card.

## Fingerprints and staleness

A fact card's fingerprint is the first 8 hex digits of SHA-256 of its
whitespace-normalized `## Statement` and `## Proof`. An explanation card is
**STALE** when an anchor differs from the current fingerprint: the fact changed
after the prose was written. `check` lists stale cards; after the author has
reread the text, `anchor ID` records the current fingerprints. `impact ID`
lists every fact depending on `ID` and every prose card to reread.

## Structure

```
title: ...
external: [cited-result]     # prerequisites the paper cites instead of showing
sections:
  - title: Graded sets
    items:
      - x-why-grade                          # explanation card, printed as is
      - def-graded-set
      - {card: thm-grading, proof: author}   # fact | author | omit | appendix
appendix:
  - lem-technical
```

Without an option a proposition shows the author's proof when one exists,
otherwise the reference proof (marked by a TeX comment). `check` reports
unknown or duplicated ids, prerequisites shown later (`FORWARD`, or appendix),
prerequisites not shown at all (`MISSING`) and fact cards no section uses
(`UNUSED`).

## Commands

Run `scripts/cards.py` of this skill from inside the harness or with `--root`.

```
python3 <skill>/scripts/cards.py init writing/<paper>/harness
python3 <skill>/scripts/cards.py check [--json]
python3 <skill>/scripts/cards.py status
python3 <skill>/scripts/cards.py graph          # knowledge-dependencies schema v1
python3 <skill>/scripts/cards.py render [--sections N] [--out NAME]
python3 <skill>/scripts/cards.py html
python3 <skill>/scripts/cards.py read           # reading page: paper order, large type, comments
python3 <skill>/scripts/cards.py impact ID...
python3 <skill>/scripts/cards.py anchor ID
python3 <skill>/scripts/cards.py terms [FILE] [--assumed profile.json] [--json]
```

`graph` writes `dependencies.yaml` with workspace-relative source paths (the
enclosing Git root, or `workspace` in `harness.toml`), so
[knowledge-dependencies](../../knowledge-dependencies/SKILL.md) checks it:
`python3 <labo-script> dependencies check --workspace <root> --graph <harness>/dependencies.yaml`.

`render` writes `paper/cards.tex` (never `main.tex`, which would clash with a
hand-written root of the same paper). The preamble is generated for
`language` (`en`: pdfLaTeX `amsart`; `ja`: upLaTeX + dvipdfmx `jsarticle`) with
`macros` appended, or read whole from `preamble`. Build the PDF through
[labo-build](../../labo-build/SKILL.md):
`python3 <labo-script> output build --source <harness>/paper/cards.tex`.

`read` writes `read.html` next to the viewer: the paper in reading order with the
paper's numbers, proofs folded, references as links, adjustable type size and line
length (remembered by the browser), light and dark themes. The author selects text,
adds a comment and copies all comments, each with its card id and the quoted text,
to paste back to the agent. Comments stay in the browser tab. `reader_font_px` and
`reader_width_em` in `harness.toml` set the defaults.

The comments come from `assets/comment-layer.js`, which works on any HTML page
with MathJax 3 or KaTeX (formulas are quoted as their TeX source; "where" is the
card, a `data-comment-label`, or the nearest heading). Add it to another page,
for example a reading-proof-review page, with
`python3 <skill>/scripts/comment_layer.py page.html --lang ja`; the script is
inlined and a rerun replaces it.

`html` writes one static viewer (`html/index.html`) with search, status
colors, links between uses, and the warnings of `check`. With `[html_index]` in
`harness.toml` it also writes a list of every viewer in the parent of
`html_out`, so several papers can share one site directory. Put it wherever the
workspace serves private pages; it is a reading aid, not a publication.
