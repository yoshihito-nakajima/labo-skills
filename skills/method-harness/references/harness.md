# The method harness: cards, checks and the reader

`scripts/method.py` keeps a method paper as cards: claims, code steps, figures, runs and the
connective cards of each reading route. It uses the ideas of `book-harness` (a shared pool, routes,
fingerprints, STALE). `scripts/reader.py` renders the reader: a main text in paper order and the
appendices for proofs and for the correspondence between theorems and code. The page assembly
(translation source, menus, CSS) stays in each project; the harness supplies the parts and checks.

```sh
m() { python3 <skill>/scripts/method.py --root <project> "$@"; }
m check [--route R] [--info]     # errors, warnings, and intended forward references of loose routes
m status                         # counts by kind and status, routes
m search "word" / m show ID... / m list --route R / m closure ID / m impact ID / m graph --route R
m new KIND ID --title T --area A [--decision reuse|variant:<id>|new --reason ...]   # stops on a similar card
m anchor ID [--to X Y] [--all]   # record fingerprints after rereading (a step also records code.fp)
m run RUN-ID                     # run the card's command and record runs/<id>.json
m set-status ID reproduced       # refused without a valid run record
m html --route R [--name N] [--out PATH]
m fingerprints                   # JSON {card id: fingerprint} for other harnesses (reverse staleness)
```

Project layout: `pool/<area>/` (facts), `src/` (sources), `route/<slug>/` (route files, connective
cards and source maps), `runs/` (run records), `harness.toml`.

## Cards

Facts (`pool/<area>/`): `claim` (`form: notation|convention|…`), `step` (a code step; another language
is `variant_of`), `figure` (`page` required), `term`, `api`, `run`. Connective cards
(`route/<slug>/card/`, per route, no facts): `ask`, `bridge`, `preview`, `recap`, `entrance`.
Ledgers: `source` (`src/`; `code_root`, `sha256`), `map`, `finding`. Common front matter:
`id kind title status origin requires references sources relations anchors`, with
`origin = original | ai-written | ai-standin | reader`.

A figure card may carry `image` (a PNG under the project) and `alt`; the PNG is embedded in the
generated HTML (rendering figure cards needs Pillow). Rendering linked book cards needs Pandoc on
`PATH` to convert their Markdown and mathematics to HTML and MathML. When a source card's `file` is a local PDF and a card's `sources` entry has
`pdf_page` (counted in the file), the page is linked; `loc` holds the reader-facing locator.

## Status ladder and staleness

`stated` (copied) → `traced` (matched with the source) → `reproduced` (run) → `checked`
(independently confirmed). `reproduced` and above need `evidence` (run cards) with a valid record.
A step stores the fingerprint of its code lines (`code.fp`): a change gives `CODE-CHANGED`, cards
anchored to the step become `STALE`, and its run records `STALE-RUN`. A run's fingerprint includes
its record (exit code, output fingerprint, file fingerprints, whether the record still matches the
code), so rerunning with a different result makes citing text `STALE`. `anchor` and `run` clear them.

## Routes

`route/<slug>/route.yaml`: `order: strict | free`, `includes`, `sections[].items` (an id or
`{card, show: gist|full}`). In a `strict` route a prerequisite placed later is `FORWARD` (error); in a
`free` route (code order and the like) it is `FORWARD-OK` (`--info` lists them). The route HTML
switches between overview, reading and full views and carries the shared comment layer.

## Source passages

A `map` card may carry `passages`: each has a stable `id`, `at` (the section and one of
`heading: true`, `paragraph`, `equation`, or `algorithm` with `step`), a `summary`, `links` to
figures, mathematics, code, runs, claims, book cards and open sources, and `reading`, the order in
which they are read: `{text: …}` and `{ref: key}` (`{ref: key, part: code}` for the code part of a
mathematical card). Paragraphs are counted from 1 over the top-level paragraphs of the translation.
Figures carry panels and crops, code links carry `line` and `through`, and local cards are anchored
in `anchors`. Mathematics uses `namespace:fact-id` of a `writing-harness` registered under
`[writing_harnesses]`, with that harness's fingerprints. `source_note` records an error or remark on
the source text; `probe` holds a hand calculation for the reader. After rereading a correspondence,
`anchor MAP-ID` records the fingerprints.

`[reader]` options in `harness.toml`: `inline_figures`, `ordered_reading`, `structured_facts`
(`## Setup`, `## Proof`, `## In code` with `reader_code` on writing-harness facts), `fold_evidence`
(not with appendices), `code_proofs`, `source_regions`, `claim_readings`,
`require_code_walkthroughs`, `appendices`, `require_points`, `require_realizations`,
`max_main_per_section` (default 2), `require_lineage`, `paragraph_ledger`.

## Statements of each passage

`[reader].claim_readings` names a YAML file mapping each passage ID to its statements. Each has `id`,
`kind`, `title`, `statement` and `reason`; `requires` lists earlier statements of the passage and
`basis` the keys of its links; unfinished justification is `status: open` with the remaining work in
`reason`. Kinds:

- `definition`, `math`: textbook statements with a closed formula in `formula` and a `point`.
- `cost`: a complexity statement. `model` states what counts as a step, the input sizes, the algorithm
  and whether the bound is upper, lower or tight. When the source states a cost without fixing the
  algorithm, split it by algorithm and separate what holds for the method itself.
- `observation`: what a figure or run shows, with the figure or run in `basis`.
- `cited`: a statement whose support is cited work rather than a proof here; needs `origin`.
- `code`: what lines of code do, with the code link in `basis`.

`point` is one or two sentences that read as the outline of the proof (for a definition, its role).
`main: true` marks the key statements of a section (checked `definition` or `math` only, at most
`max_main_per_section`); they appear numbered in the main text.

### Origin: comparing the source with the original work

Any statement may carry `origin`: `{src: source card or cite: bibliographic text, loc, pdf_page,
relation, note, substitute}`. `relation` is `agrees`, `hypotheses` (agrees once hypotheses are added),
`stronger` (the source says more than the original), `weaker`, `differs` or `unchecked`; any relation
other than `agrees` and `unchecked` needs a `note`. When the original is paywalled or the source gives
no citation, use an openly accessible substitute that states the result and cites the original (a
survey, a later paper, the library's code) as `src`, and write in `substitute` why it replaces the
original; the pages mark it as a substitute. Only when no substitute exists, use `unchecked` and keep
the statement `open`. Errors in the source's own text go to the passage's `source_note`.

### Statements in textbook form

`statement` is the text the reader sees: sets and map types, ranges of variables, hypotheses and
conclusion in one piece; quantifiers may be written in words; central equations displayed. `reason`
holds the proof. `definition`, `math` and `code` statements also carry the closed formula `formula`,
which the harness checks for notation and variable scope:

```yaml
statement: >-
  Let $a,b\in\mathbb R$ with $a\le b$. Then
  $\{x\in\mathbb R:x\le a\}\subseteq\{x\in\mathbb R:x\le b\}$.
formula: 'a:\mathbb{R}; b:\mathbb{R} :: @a\le @b\implies \setof{x}{\mathbb{R}}{@x\le @a}\subseteq\setof{y}{\mathbb{R}}{@y\le @b}'
```

Before ` :: ` come the outer universal bindings `name:set` separated by semicolons (`X:*` for an
arbitrary set); variables are referred to as `@name`. Inner bindings: `\all{n}{S}{P}`, `\some`,
`\one`, `\setof{n}{S}{cond}`, `\sumover`, `\limto`, `\fn`; operators `\op{rank}`, predicates
`\pred{Open}`. Whether the formula matches the statement is checked by reading.

## Code walkthroughs

A code link may carry a `walkthrough`, read in execution order:

```yaml
role: code
card: step-toy-square
key: square
line: 2
through: 3
text: Returns the square.
walkthrough:
  claim: multiply-entry          # a kind: code statement of the passage; its basis contains this key
  bridge: If $x$ is a real number, the returned product is $x^2$.
  math: [square-nonnegative]     # kind: math statements in dependency order
  realization:
  - math: the square $x^2$
    code: line 2, \texttt{x * x}
    kind: equality               # equality | approximation (needs error) | numerical | choice
    holds: \texttt{x} holds a finite real number.
    outside: rounding.
```

`bridge` proves that what the lines do becomes the mathematical object or hypothesis used by the
statement. `realization` is the table between theorem and computation; it is part of the
walkthrough's fingerprint, so a change gives `STALE-PASSAGE`. `require_code_walkthroughs` and
`require_realizations` make them mandatory.

## Lineage of code cards

A step card carries `lineage`; `require_lineage` makes it mandatory for code used in walkthroughs:

```yaml
lineage:
  proposal: {src: src-primary, loc: "§7, eq. (7.18)", pdf_page: 13}   # the work that proposed the step
  intent: "Why the proposers chose this step, paraphrased from that passage."
  code: ai              # author | library | reader | ai
  follows: "The implementation followed (optional)."
  differences: "Departures from the proposal: defaults, omitted steps, regularization, stopping rules."
  status: checked       # open when the proposers' words have not been checked
  substitute: "Why a substitute replaces a paywalled or missing original (optional)."
```

The lineage is not part of any fingerprint. The reader shows it at the head of each code card in
Appendix B and tables it by proposing source in Appendix D.

## Main text and appendices

With `[reader].appendices = true` the reader follows the order of a method paper, with the section
order taken from the `structure.yaml` of the registered writing harness. Each source section or
subsection folds under its heading, nothing deeper; the main text starts open, the appendices closed,
and a link opens its target's section. Each long text lives in one place, other pages carry a short
guide and a link:

| Content | Place | Guide elsewhere |
| --- | --- | --- |
| Key statements with their point | Main text | "proof outline in the main text, Proposition 4.7" at the head of the Appendix A item |
| Proofs | Appendix A | the proof outline (`point`) and the number |
| Computation and code | Appendix B | the code flow (the titles of the Appendix B steps in order) |

- Main text: the translation with figures in place and the `main: true` statements after their
  paragraph or equation, numbered by chapter in text order (`PassageViews.set_text_order`), each with
  its proof outline and the passage's code flow. Algorithm steps get "▷ Proposition 4.3 · B.10.1".
- Appendix A (`proofs_sections`): per passage, its code flow, the reading (figures, book cards, open
  sources, mathematical cards, step numbers) and all its statements, numbered (main ones keep their
  number; others are Lemma A.n), each with a lead, the statement, premises, proof, origin and where it
  is used.
- Appendix B (`methods_sections`): per source section, each code card used there (B.k) and its steps
  (B.k.j): proof outlines of the statements used, the code claim, the correspondence table, the
  bridge, alternative derivations and the code. `outside_theory` lists every row that is not an
  equality.
- `relink` sends in-text links (`\href{#…}`) to the page that now holds the target;
  `lineage_table`, `origins_html` and `coverage_html` render the Appendix D tables.

## Paragraph coverage

`[reader].paragraph_ledger` names a YAML file; the build then checks every paragraph of the
translation. A paragraph is read in a passage (`at.paragraph`, or `at.equation` for the paragraph
holding the equation) or recorded in the ledger; figure and caption positions are skipped.

```yaml
"4.2.1":
  2: {none: "Heading of the algorithm.", fp: 6ebf0a44}
  1: {passage: isomap-mds, fp: deaf176c}
```

`none` gives the reason the paragraph holds no claim; `passage` names the passage that handles its
claim. `fp` is the fingerprint of the paragraph text, so a changed translation reopens it. A ledger
entry for a paragraph that has a passage, or for a missing paragraph, is an error.
`PassageViews.check_paragraphs` checks and `paragraph_coverage` reports how each paragraph is handled.

## Reverse staleness

`m fingerprints` prints the current fingerprint of every card. A writing harness lists cited code,
runs and figures under `evidence: [ns:id]` and registers
`[evidence.ns] command = ["{python}", "<skill>/scripts/method.py", "--root", "<project>", "fingerprints"]`,
so that its prose becomes `STALE` when the cited code or result changes (see the writing-harness
`references/cards.md`).

## Book cards and open sources

Mathematics comes first from book cards. Register `[book_harnesses.<ns>]` with `root` (a book root
under the workspace's `local/`) and `route`. A `role: book` link has `card: <ns>:<card-id>`,
`version: sha256:…` (from `labo book borrow CARD --route ROUTE --root ROOT`), `key` and `text`; the
reader renders the card and the route's proof at the point of use. A change to the card, the chosen
proof or its prerequisites gives `STALE-PASSAGE`.

New sources are adopted only when the text can be opened at the official host and the terms fit the
use. Paywalled, private, login-gated or unclear sources are not taken in. An open source is a local
`source` card with `access: open`, `edition`, `url`, `license`, `license_url` and `checked`, linked
with `role: source` and `loc`. Original PDFs, OCR and page images stay in local storage outside every
Git.

## Source facsimiles per section

`[reader].source_regions` names a JSON file: `source` (the source card), `sha256` of the local PDF,
and `sections` mapping each section ID to regions `[PDF page, left, top, right, bottom]` in PDF points
from the top left, in reading order. `source_images.py` checks the fingerprints and pages, renders
the regions with Poppler's `pdftoppm` and Pillow, and gives each section links that open each region.
