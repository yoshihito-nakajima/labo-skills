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

## Facts from another harness

A paper that builds on a companion paper's cards names them as `ns:id` in
`requires`, with the namespace declared in `harness.toml`:

```
[external_harnesses]
ctg = "../../compact-target-gds/harness"   # relative to this harness
```

`check` accepts `ns:id` when that harness has `cards/*/id.md`, and reports it
otherwise. Such cards are cited, never rendered here; list them under
`external:` in `structure.yaml` once the structure exists.

For a result borrowed from another paper or found through a book or lecture card, apply the
[result reuse check](../../knowledge-dependencies/SKILL.md#reuse-a-result-across-artifacts). Use the existing
`source` field and notes to record the owner, exact locator and version, the form used and the prior review scope
if known. Check the paper's application and any change to the proof in the paper's own review. Use `ns:id` for
companion paper harnesses with the documented layout. For book cards, record their provenance in the card notes
and give the appropriate mathematical citation in the manuscript. If a reused statement or proof is adapted,
record the difference and the uses it affects.

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
    label: sec:graded                        # optional; emitted as \label after \section
    items:
      - x-why-grade                          # explanation card, printed as is
      - def-graded-set
      - {card: thm-grading, proof: author}   # fact | author | omit | appendix | later
      - {card: thm-main, proof: later}       # statement first ...
      - lem-step
      - {proof_of: thm-main}                 # ... its proof after the lemmas it uses
      - {subsection: Proofs, label: sec:proofs}  # a numbered subsection heading (label optional)
appendix:
  - lem-technical
```

Section and subsection labels let explanation cards refer to sections with
`\ref` or, with `ref_command = "Cref"` in `harness.toml` and cleveref in the
preamble, with `\Cref`; the same setting renders bare card ids as `\Cref`.

Without an option a proposition shows the author's proof when one exists,
otherwise the reference proof (marked by a TeX comment). `check` reports
unknown or duplicated ids, prerequisites shown later (`FORWARD`, or appendix),
prerequisites not shown at all (`MISSING`) and fact cards no section uses
(`UNUSED`).

`proof: later` prints only the statement; the proof appears at the
`{proof_of: ID}` item, headed with a reference back to the statement. Use it to
state the section's main results first. Prerequisites are checked against the
position of the proof, so the lemmas may sit between the two.

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
python3 <skill>/scripts/cards.py build [--no-pdf]   # check + render + PDF + html + read
python3 <skill>/scripts/cards.py watch [--no-pdf]   # background build on every source change
python3 <skill>/scripts/cards.py hook               # Claude Code PostToolUse hook
python3 <skill>/scripts/cards.py new KIND ID [--title T] [--requires A,B] [--explains X,Y]
python3 <skill>/scripts/cards.py serve [--port P]   # reading page + card editor
```

`build`, `watch`, `hook`, `serve`, `new` and the `OUTDATED` warning are
described in [outputs and the editor](outputs-and-editor.md).

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

### Reading page

`read` writes `read.html` next to the viewer with the paper in reading order and the
paper's numbers, proofs folded, references as links, adjustable type size and line
length (remembered by the browser), light and dark themes. The author selects text,
adds a comment and copies all comments, each with its card id and the quoted text,
to paste back to the agent. Comments stay in the browser tab. `reader_font_px` and
`reader_width_em` in `harness.toml` set the defaults.

The [book reader](../../book-harness/references/views.md#reader-facing-html) follows the same reading layout.
The comment layer in `assets/comment-layer.js` works on any HTML page
with MathJax 3 or KaTeX (formulas are quoted as their TeX source; "where" is the
card, a `data-comment-label`, or the nearest heading). Add it to another page,
for example a reading-proof-review page, with
`python3 <skill>/scripts/comment_layer.py page.html --lang ja`; the script is
inlined and a rerun replaces it.

### Card viewer

`html` writes one static viewer (`html/index.html`) with search, status
colors, links between uses, and the warnings of `check`. With `[html_index]` in
`harness.toml` it also writes a list of every viewer in the parent of
`html_out`, so several papers can share one site directory. Put it wherever the
workspace serves private pages; it is a reading aid, not a publication.
