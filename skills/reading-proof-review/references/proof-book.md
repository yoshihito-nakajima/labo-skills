# Proof-centred reading page and PDF

A second output of this skill, next to the review page. Use it when the user wants to **follow the proof itself**:
every formula transformation traceable, the proof cut into a few blocks, the difficulty and the reason for each
piece visible, and a PDF that carries the full derivation. It is for understanding, not a paper and not a certificate.

## What it produces (one command)

`python3 <scripts>/proof_book.py build <project>` writes into `<project>/<out>/`:

- `<prefix>.pdf` — one PDF: contents, the problem and its difficulties, then every block with its role, every step
  with a context box, and the full derivation (reason → formula, blue automatic numbers, bookmarks).
- `<prefix>.html` — the same content as one page (main line only; very fine lines are replaced by a link to the PDF).
- `<prefix>-block-<ID>.html` — the same blocks as separate pages, each with links back to the combined page and the index.
- `<prefix>-index.html`, `pages.json`.

`check <project>` runs the LaTeX log, KaTeX render, anchor and PDF-margin checks (headless Chrome and PyMuPDF are
optional; a skipped check is reported as skipped). `refs <project> --block X` prints, for each line whose lead cites
another line, the cited formula, so citations can be read at a glance.

## Project directory

```
book.json      {"title", "prefix", "order": ["A","B",...], "blocks_dir", "ledger", "context", "out", "builder"}
blocks/X.txt   one derivation source per block (below)
context.json   problem, difficulties, block roles, step reasons (below)
ledger/steps.json   optional; shows tier/origin as a provisional classification
```

Block ids are single capital letters or any short capital string; they become section names and equation prefixes
(`X.2.3` = third displayed line of step 2 of block X). Cross-block citations are written in words,
`ブロック D・段 3`; the HTML turns them into links and the PDF into hyperlinks. A bare `D.3` inside block D is a link to its own step.

## Block source format

```
block: D            step: D.1
title: ...          title: ...
claim: ... $math$   ledger: D3a            (optional ledger id)
loc: manuscript locator
> shared prose (HTML and PDF)             step also has: claim: ..., loc: ...
>> narration: a paragraph that plans or recaps (HTML can hide it)
- TeX @@ lead @@ flags
```

- **lead** is the clause printed *before* the formula and ends in a connective ("…なので、"). A page is a flow
  *reason, formula, reason, formula*; no right-hand reason column, no "∵" list, no table.
- **flags**: `fine:topic` = routine and long: the PDF has the line, the HTML shows one link row for the whole run;
  `recon` = added by the page author, not in the manuscript (marked †; the expansion must be checked by an independent reader).
- A continuation line starts with a relation (`\le`, `=`, ...) and joins the previous formula's chain.
  `\newrow` inside a line forces a typographic break at that point (the HTML ignores it). A row that overflows the page
  is split automatically at its relations on the second build.
- **Numbers only for cited formulas.** Write `(D.2.6)` in any lead, prose or claim to cite line 6 of step D.2; that
  line then gets an automatic number, identical in HTML and PDF (the build fails if they differ). Lines nobody cites have
  no number. Citing a `fine` line is refused, because the HTML hides it.
- Every step needs a `claim:`; narrate in the user's language. Math is TeX in `$...$`; do not put ` @@ ` inside a formula.

## Grouping into blocks

Group ledger steps into 6–9 blocks that each answer one question (tools; approximation and bounds; limit; the cut-off
device; the key lemma; closing). Keep the ledger at atom size; blocks are a presentation layer. Reading order = `order`.
A block's steps should lean on earlier blocks only, and every citation of another block names the step.

## Context layers (context.json)

Three layers, all hand-written and checked like any claim:

- `page`: `setting`, `goal` (what is and is **not** shown), `strategy` — lists of paragraphs. Say "the manuscript claims"
  for any novelty; never assert it before the prior-work stage.
- `diffs`: numbered difficulties `{"title","text"}` — *why the obvious route fails*, not merely what is hard.
- `block[ID]`: `role` and the `diffs` it answers; `step[ID.n]`: `why` this step is needed here and the `diffs` it serves.
  "Used by" and "relies on" lists are computed from the citations, not written.

## Review layer (review.json, optional)

The reading page and the PDF show what was reviewed, how far it holds and what looks risky, in three places: a front
section "査読の結果と、危うい点", a box per block, and a line in each step's context box. Everything is written in
`review.json` (set `"review"` in `book.json`); `check` verifies ids, levels and statuses.

- `verdict`: `summary` (the range actually checked, never "correct"), `cannot_say` (limits: language-model checkers,
  no formal check, prior art unsettled), `indicator` (`label`, `why`; rule-capped).
- `panel`: one entry per independent viewpoint: `key` (`audit`, `counter`, `numeric`, `prior`, `hostile`, ...),
  `short`, `title`, `how`, `what`, `covers` (block ids or step ids), `result`. The step line "検査 ... 数値確認" is
  computed from `covers`; a step outside every `numeric` entry is shown as "未実施（解析的な段）".
- `risks`: `id`, `level` (`high|mid|low`), `title`, `why`, `safe_if` (what would settle it), `where` (step ids).
- `findings`: `id`, `level` (`major|minor|expr`), `status` (`fixed|supplement|open|noted`), `where`, `text`, `fix`,
  `source`, `certain` (false = suspected). `fixed` = the blocks were changed; `supplement` = not repairable on the page,
  the manuscript needs the change (also write it under `supplements`); `open` = unresolved.
- `supplements`: what the manuscript itself should say; `block[ID]`: a one-line note per block.

Loop to run before building: independent panel -> parent merges findings (confirmed vs suspected) -> repair the blocks
and re-check the repaired lines with a fresh checker (at most three rounds) -> whatever cannot be repaired becomes a
`supplement` or `open` finding. Never change the manuscript's claim to make a line pass; report it.

## Writing the derivation: how to avoid gaps

- Every formula change is a line; the lead says which rule, which earlier line, which hypothesis. If a reader could not
  do it in one routine step, add a line. Index shifts, empty sums, range of `n`, the sign of each coefficient and the
  direction of each inequality are stated, not implied.
- State the case split and the order of limits explicitly (fixed parameters, which limit first).
- Where the manuscript is shorter than the page, mark the added lines `recon`; where the page uses a constant different
  from the manuscript, say so in the lead and check that it is valid.
- Do the algebra by hand for every index-heavy identity before handing the blocks to a checker.

## Check before handing over

1. `build` then `check`; zero log problems, zero KaTeX errors, zero dangling anchors, zero margin overflow.
2. `refs` per block: each citation points at the line the lead needs.
3. Independent read: give each block (or two small ones) to a fresh, read-only checker
   (see [proof-adversarial-review](../../proof-adversarial-review/SKILL.md), role "line-by-line audit" / "independent verification")
   with the manuscript as authority; ask for line-level findings with severity. Fix, rebuild, and keep the report in the
   project's private review folder. A second pass of the same kind checks `context.json` against the manuscript.
4. Fill `review.json` (above) so the page itself says what was and was not checked: hand computation by language models is not a formal proof.

## Limits

- Labels in the generated pages are Japanese; block text and context may be written in any language, but the
  document class is `ltjsarticle` (LuaLaTeX with luatex-ja). For another language, edit the preamble and the label
  strings in `proof_book.py`.
- PDF → HTML links are absolute `file://` URIs (they break if the folder is moved); HTML → PDF links are relative and
  need both files in one folder. Link clicking in a PDF viewer is not tested by the build.
- Needs `latexmk` with LuaLaTeX, `tcolorbox`, KaTeX (see `fetch_katex.py`). Source and generated pages of a real project
  stay private; only generic rules and the fictional example belong in this skill.
