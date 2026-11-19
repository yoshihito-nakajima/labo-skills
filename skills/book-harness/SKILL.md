---
name: book-harness
description: Read books into, and build books from, a shared pool of small cards — definition, claim, proof, example, exercise and convention cards used by every book — with per-book routes, lecture-note glue cards, source mappings, fingerprints, stale detection, graph views, TeX/HTML output and an intake review (self-check, verbatim check, independent review bound to fingerprints) when a source is taken in. Use to read a source into the pool, add to or join books at card level, audit or view them; source editions and adoption decisions stay with reading-book, the overall plan with course-planning.
---

# Book harness

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

A book is made of **cards**, not chapters. Facts live once, in a pool shared by all books; a book is a **route**
through the pool plus its own glue and its own map to the sources. Reading a source means adding to the pool;
building a book means choosing a route. Joining, reusing, slicing or comparing books is a question about cards.
[writing-harness](../writing-harness/SKILL.md) is the sibling for a paper the author writes.

## The rules

1. **Facts are cards, independent of any book.** One claim, definition, proof, example, exercise or convention per
   card, with a stable kebab-case id that never changes meaning.
2. **Search the pool before creating a fact card** (`book search`, then `book show`; `book new` refuses without a
   decision, under a lock). Same statement → reuse. Different hypotheses, quantifiers or normalization → a new card
   with a relation that says what differs. Alike names are not a match; compare hypotheses.
3. **Cards are the canonical text; TeX and HTML are generated** and not tracked. Never keep a second editable text.
4. **`requires` belongs to a statement and to its proof**, never to a book. Proof steps cite what they use as
   `[by: card-id]`; the cites equal `requires`. Text names other cards as `[[card-id]]`.
5. **Glue states no new fact.** Motivation, transitions, previews, recaps and entrances refer to fact cards by id;
   a new fact goes into a fact card. Glue is route-local and anchored to its neighbours.
6. **Fingerprints decide what to reread.** A changed card makes every card anchored to it STALE; an independent
   review applies to the fingerprint it was recorded against and never carries over to a changed card.
7. **Completion is a query** (`book status`): `complete` is every source mapping OK or OUT with no open major finding
   and no error; `taken in` adds a current math review of every fact card. Report which one you mean. Page counts and titles are not evidence.
8. **Cards carry locators, never original text.** Write in the book's own words; originals, OCR and page images stay
   outside every Git and out of cards, packets and reports. Card text is course material: it is not sent outside the
   machine, private remotes included.
9. **Work on a card and its neighbourhood**; a frozen input for review is a list of ids with fingerprints.
10. **Taking a source in ends with the intake review**, not with the last card: self-check, mechanical gates
    (including the verbatim check) and a bounded independent review of the new and changed cards. Report what was
    not independently reviewed as not done.

## Start or resume

1. Find the book root (default `local/materials/book/`: `pool/`, `src/`, `route/<slug>/`; it sits inside the guarded
   local materials Git, whose guard tooling names `materials/`, so it is not a separate Git). A project that has only
   TeX and a catalog is [migrated](references/migration.md) first, as a read-only mirror until the owners agree to cut over.
2. Run `book check --route R` and `book status --route R`; report errors, STALE cards, forward references, unlisted
   borrows, open findings and review coverage before new work.
3. Take the next unit from the route and its source mapping (`TODO` rows), not from a prose log.

## Work

- Taking a book in, unit by unit (read, search the pool, write cards, map the source):
  [reading loop](references/reading-loop.md). Then [intake review](references/intake-review.md).
- Card formats, the 14 templates, variants and what each check enforces: [templates](references/templates.md).
- Pool search, relations between books, routes, `includes`, show levels, borrows: [pool and route](references/pool-and-route.md).
- Tidying a large pool — merge, rename, retire, legacy cards, dependency candidates, concurrent writers, scale:
  [pool operations](references/pool-operations.md).
- Graph and HTML views, slices, queries across books: [views](references/views.md).
- Rendering TeX, references, a whole document, building: [building](references/building.md).
- Running the intake unattended with a light coordinator and capable workers, on any LLM host: [rounds](references/rounds.md).
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
labo book render --route R --level L3 [--standalone --language ja] --out FILE
labo book html --route R [--slice closure:ID] [--candidates] --name NAME
```

After any change to cards or a route run `check`; before changing a statement run `impact` and say which cards and
glue to reread. A change to a shared card concerns every route that uses it. Build PDFs through the project's build
path ([course-authoring](../course-authoring/SKILL.md)); the tool checks structure, fingerprints and text overlap,
not mathematics. Mathematical review is separate: [reading-book-math-review](../reading-book-math-review/SKILL.md).
