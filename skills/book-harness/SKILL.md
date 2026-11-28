---
name: book-harness
description: Read a specified source or mathematical topic into a route through a shared card pool. Use to assemble, revise, join or audit mathematical books and lecture notes, with source mappings, versioned reviews, and TeX or HTML output.
---

# Book harness

Take responsibility for the scope assigned to one book. The request can specify source material, a mathematical topic, or both.
Use one **route** for the scope and reading order, and one pool of fact cards shared across books. The basic result is
section headings and an ordered list of cards. Book-length routes can attach explicitly planned
chapters to sections. Generate the book PDF's chapter and section numbers from route placement.
Keep production work units as separate metadata and use stable section IDs.
For work across books, apply the [versioned prerequisite rules](references/pool-and-route.md#prerequisites-from-another-book).
[Route structure and planning](references/pool-and-route.md#chapters-sections-and-work-units) covers the format. Add route-local introductions, questions, transitions and recaps as
the requested format calls for them, including when arranging the route as a series of lectures.

Follow the [role boundaries](../research-router/references/editing-capability.md). The light coordinator handles
progress and handoffs; substantive reading, writing and judgment belong to the assigned workers.
[writing-harness](../writing-harness/SKILL.md) supports the author of a card-based paper. For results shared between
books and papers, use the [reuse check](../knowledge-dependencies/SKILL.md#reuse-a-result-across-artifacts).

## The rules

1. **Facts are cards, independent of any book.** One claim, definition, proof, example, exercise or convention per
   card, with a stable kebab-case id that never changes meaning.
2. **Search the pool before creating a fact card** (`book search`, then `book show`; `book new` refuses without a
   decision, under a lock). Same statement → reuse. Different hypotheses, quantifiers or normalization → a new card
   with a relation that says what differs. Alike names are not a match; compare hypotheses.
3. **Cards are the canonical text; TeX and HTML are generated** and not tracked. Keep the conditions, exceptions
   and explanations the reader needs in the reader-facing output. Make text corrections in the cards and regenerate.
4. **`requires` belongs to a statement and to its proof**, never to a book. Proof steps cite what they use as
   `[by: card-id]`; the cites equal `requires`. Text names other cards as `[[card-id]]`.
5. **Glue states no new fact.** Motivation, transitions, previews, recaps and entrances refer to fact cards by id;
   a new fact goes into a fact card. Glue is route-local and anchored to its neighbours.
6. **Fingerprints decide what to reread.** A changed card makes every card anchored to it STALE; an independent
   review applies to the fingerprint it was recorded against and never carries over to a changed card.
7. **Close the agreed route.** Check its scope, current math review coverage and reading order. For assigned source
   material, also confirm adoption and source coverage. [Review and closure](references/intake-review.md#5-route-closure)
   explains what `book status` covers and what to confirm from the route plan.
8. **Cards carry locators, never original text.** Write in the book's own words; originals, OCR and page images stay
   outside every Git and out of cards, packets and reports. Card text is course material: it is not sent outside the
   machine, private remotes included.
9. **Work on a card and its neighbourhood**; a frozen input for review is a list of ids with fingerprints.
10. **Review as you work.** Self-check each new or changed card, independently review related groups in a fixed
    version, and check the assembled route at the book boundary. Check for verbatim runs when taking source text in.

## Start or resume

1. Find the book root (default `local/materials/book/`: `pool/`, `src/`, `route/<slug>/`; it sits inside the guarded
   local materials Git, whose guard tooling names `materials/`, so it is not a separate Git). A project that has only
   TeX and a catalog is [migrated](references/migration.md) first, as a read-only mirror until the owners agree to cut over.
2. Record or recover the requested scope, any assigned source ranges, the reader's allowed starting facts, the
   endpoint and the deliverable. Use [course-planning](../course-planning/SKILL.md) for book design and
   [reading-book](../reading-book/SKILL.md) for source edition, adoption and proof obligations.
3. Run `book check --route R` and `book status --route R` to recover errors, stale cards, forward references,
   unlisted borrows, open findings and review coverage. Choose the first unfinished unit in the route plan and use
   its C2 mappings where applicable. Use the existing plan or scope record for units without C2 rows.

## Work

- Use one route workflow from [reading and writing](references/reading-loop.md) through
  [self-check, independent review, repair and closure](references/intake-review.md). One coordinator can carry
  the route through the cycle. Give independent reviewers fixed inputs in a fresh context and return their
  findings to the producer for repair and recheck.
- For Japanese books and lecture notes, use the [writing rules](references/writing-rules.md) for fact cards, route prose and self-reading.
- Card formats, the 14 templates, variants and what each check enforces: [templates](references/templates.md).
- Pool search, relations between books, routes, `includes`, show levels, borrows: [pool and route](references/pool-and-route.md).
- Tidying a large pool — merge, rename, retire, legacy cards, dependency candidates, concurrent writers, scale:
  [pool operations](references/pool-operations.md).
- Give readers the shared book/paper reading layout with `book read`. Use `book html` for card searches and
  dependency inspection. See [views](references/views.md) for local output and comment handoff.
- Read [building](references/building.md) before the first reader-facing PDF. It connects the cards to the
  project's actual build, typed references, colors, indexes and output checks.
- Running source-backed units unattended, including the live parent-model check and bounded handoffs: [rounds](references/rounds.md).
- Moving existing TeX and catalogs into cards: [migration](references/migration.md).
- Complete card shapes, one of each kind: [examples](references/examples.md); every `check` code: [check codes](references/check-codes.md).

Commands (`<labo-script>` is the checkout launcher `scripts/labo.py`). `--workspace DIR` and `--root DIR` come **after**
the action, as in `labo book check --route R --workspace W --root book`; the root defaults to `local/materials/book`. Card file
shapes: [examples](references/examples.md).

```sh
labo book check [--route R]                  # errors and warnings
labo book status [--route R]                 # counts, review coverage, `complete`, `taken in`
labo book search "<words>" [--kind A2]       # pool search, before creating a fact card
labo book show ID...                         # a card with its neighbourhood
labo book list [--route R] [--kind K] [--stale] [--legacy]
labo book new KIND ID --title T --area A [--decision reuse|variant:<id>|new --reason ...]
labo book new A3 ID --proves CLAIM [--decision alt --reason ...]
labo book new D1 ID --route R --target CARD --severity major|minor --summary "..."
labo book place ROUTE ID... [--section T] [--after ID]   # put cards in the route
labo book anchor ID...                       # after rereading what the card depends on
labo book closure ID... [--candidates]       # what it needs
labo book impact ID... [--candidates]        # what to recheck
labo book merge KEEP DROP [--apply]
labo book rename OLD NEW [--apply]
labo book retire ID --reason ... [--apply]
labo book restructure ID                     # a legacy card into the template's sections
labo book deps [--route R] --write           # dependency candidates; first
labo book promote ID [--only a,b]            # then settle them
labo book reject ID [--only a,b]
labo book review-input --route R --out DIR [--unreviewed math] [--section N | --cards a,b | --closure X] [--max-chars N]
labo book record-review --manifest M --report FILE --result pass|findings [--ids a,b]
labo book review-input ... --cards-file FILE   # also: ids from a file
labo book record-review --packet PACKET      # a reviewer's result file ending in `RESULT: pass|findings`
labo book next --route R --role producer|reviewer|all --review-dir D --work-dir W --source-text DIR --claim HOLDER
labo book release UNIT [--done]               # a worker frees its unit
labo book leak-check --route R --source-text DIR [--source-text DIR ...]
labo book graph --route R
labo book outline --route R                  # chapters, sections and one row per placed card
labo book render --route R --level L3 [--standalone --language ja] --out FILE
labo book read --route R [--name NAME] [--mathjax-bundle FILE]
labo book html --route R [--slice closure:ID] [--candidates] --name NAME
```

After any change to cards or a route run `check`; before changing a statement run `impact` and say which cards and
glue to reread. A change to a shared card concerns every route that uses it. Build PDFs through the project's build
path ([course-authoring](../course-authoring/SKILL.md)); the tool checks structure, fingerprints and text overlap,
not mathematics. Mathematical review is separate: [reading-book-math-review](../reading-book-math-review/SKILL.md).

For a numbered card book, apply the [equation and index rules](references/building.md#reader-facing-build) in the route and writer handoff. Preserve stable targets when cards move across sections.
