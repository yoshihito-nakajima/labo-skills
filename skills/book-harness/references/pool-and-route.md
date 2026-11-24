# Pool, routes and joining books

## Layout

```
book/
  pool/<area>/<id>.md          fact cards A1-A6, shared by every book
  src/<id>.md                  source records C1, shared
  route/<slug>/route.yaml      sections, order, what is shown, includes
  route/<slug>/card/           glue B1-B5 of this book
  route/<slug>/map/            source mappings C2
  route/<slug>/finding/        findings D1
```

Ids are unique across the whole root. Prefix glue ids with the book (`intro-glue-1`).
Generated output (TeX, HTML, PDF) goes to the project's cache/output, never into the root.

## Pool first

Before a fact card is created, search for it: `book search "<words, symbols, old names>"`, with
several queries (the matcher is lexical). `book new` for an A card runs the same search and stops
when a similar card exists; the caller must state one of

- `--decision reuse` — the same statement; nothing is written, the route simply lists the card;
- `--decision variant:<id>` — hypotheses, quantifiers, domain or normalization differ; the new
  card gets a `variant` relation to `<id>` and must say what differs;
- `--decision new --reason "<why none fits>"` — recorded in `searched:`.

A proof is created with `book new A3 <id> --proves <claim>`: the first proof becomes the owner; a second needs
`--decision alt --reason "<what it adds>"` and is not the owner. The search compares cards of the same kind.

The search is a prompt to compare hypotheses and quantifiers, not an equivalence test. Same name
with different hypotheses is a different card; the same claim with a different proof is the same
claim card with another A3 (`owner: false` for the alternative).

## Mapping sources to cards (at creation time)

Reading a source unit, in the order of the book: find or create the cards, then write its C2
at once: relation (same, implies, special-case, variant, alt-proof, equivalent), adoption and
scope audit. Several sources for one claim are several C2 rows pointing at one card. C2 tracks source coverage.
Use the route's existing plan or scope record for its agreed units and endpoint, including work assembled from
existing cards. See [route closure](intake-review.md#5-route-closure) for the two kinds of evidence.

## Routes

```yaml
title: Parity A
includes: [prelim]            # earlier routes, in order; the cards are shared, not copied
sections:
  - title: Even
    items:
      - entrance-a             # a card id
      - {card: claim-parity, proof: later}   # owner | later | omit | appendix | <A3 id>
      - {proof_of: claim-parity}             # its proof, after the lemmas it uses
appendix: [lem-technical]
```

- The sequence is what the reader sees. Follow source order where the request calls for it, or arrange the
  cards to reach the agreed endpoint. Group the sequence by lecture when requested. Every card's `requires`
  (and cited conventions) must come
  earlier in the sequence or be listed under `borrows` in an entrance card of the route.
- A claim shows its chosen proof right after it unless `proof` says otherwise; `later` places
  it at `proof_of` (list `proof_of` only for a claim marked `proof: later`, or the proof appears twice and `check`
  warns `DUPLICATE-IN-ROUTE`). A different proof for this book is chosen with `proof: <A3 id>`.
- **Joining books**: a route that `includes` others plus its own sections and glue is the joint
  book; reading order, glue and entrance are its own, cards are shared. A card has one owning
  proof in the pool; other books cite or choose an alternative explicitly.
- **Glue between joined parts** is a B2 between the last card of one part and the first of the next.
- Symbols that two cards use differently are a conflict when joined: settle it in an A6
  convention or a variant, not in the glue.

### Prerequisites from another book

Each book owns its route, including chapter and section order. Card IDs identify the mathematical
statements shared across books. Establish the dependency with `requires` and cite the card ID in
the invoking passage. Printed chapter, theorem and equation numbers are generated at build time.

If the result must be reachable by an internal PDF link, place the applicable shared card in the new
route before its first use. For a result treated as prior knowledge from an earlier book, list it once
in a B5 entrance card's `borrows`. Record the owning route, an exact version, and the reason for using
it. Give readers the owning book title or source locator in the entrance. `[[card-id]]` and
`[by: card-id]` render a borrowed item's title in a standalone book. Use those forms for the item;
the build uses local labels for links to material placed in the current book.

Use `strict_borrows: true` for new multivolume routes. An entry naming a concrete owning route
also enables version checks. The earlier `owner: pool` form is available for existing unversioned
routes. A new cross-volume entry has this shape:

```yaml
borrows:
  - card: thm-quotient-factorization
    owner: first-book
    version: sha256:<generated digest>
    why: The factorization is the input to the induced map.
```

Generate the corresponding three identity fields with
`python3 .agents/scripts/labo.py book borrow CARD --route OWNER`. Compare the hypotheses,
conventions and conclusion with the actual use, and record the owning review and its scope in the
handoff before adopting that version. The command computes the version from the placed card,
the proof selected in the owning route, and their transitive hard prerequisites and conventions.
Each borrowed theorem needs one selected proof in its owning route. Chapter and section numbers
do not enter the version. This command identifies input; review and acceptance still require
evidence for the stated scope. Keep the old pin until the changed target, proof, and affected uses
have been reread. Use `book impact` alongside the route's precise proof and borrow records to find
uses affected by a change.

Run `book check --route DESTINATION` before freezing each dependent unit. The PDF and HTML builds
use the same route checks for versioned routes. An undeclared prerequisite or reference, a stale
version, an unavailable raw TeX label, or a local prerequisite placed after its use blocks the
build. For a deliberately joined book, declare `includes` explicitly, use unique chapter and
section IDs across the included routes, and check the joined reading order and output.


### Chapters, sections and work units

For a book with chapters, declare the chapter headings in `chapters` and attach each actual
section to its chapter. Chapter order follows the first appearance of each chapter in the section
sequence. Each chapter occupies one consecutive run of sections. The same work unit can supply multiple
sections. A section spanning multiple work units can list their IDs in `work_units`.

For a book-length PDF, use the chaptered route so the renderer generates section numbers
such as `1.1`, `2.1`, `11.1` and `A.1` from placement. Store stable IDs on cards and production
units. A card may be reused at a different position. Use the brief to decide whether individual
cards in a card view need a displayed number. See the [build rules](building.md#reader-facing-build)
for checking the book's printed contents.

```yaml
title: An introduction to paths
chapters:
  paths: {title: Paths in a graph}
  examples: {title: Longer examples, appendix: true}
sections:
  - id: walks-and-paths
    chapter: paths
    title: Walks and paths
    work_unit: draft-paths
    items: [def-path, prop-simple-path]
  - id: examples-of-paths
    chapter: examples
    title: Worked examples
    items: [ex-path-cycle]
```

Use stable, unique section IDs and mathematical headings. In the plan, give each section a
question, its input and exit results, and an ordered list with one row per mathematical item.
Each row states its role, the target card or existing ID if known, and the direct prerequisites.
Keep source-number coverage in the existing C2 records. Once placed, the route item sequence
and card records supply the exact order and proof information. Use `[by: card-id]` at a proof
step that invokes the referenced fact, and state local inferences in the prose.
The inventory comes from `book outline --route R` in Markdown or JSON. Use a stable section ID
with `book place --section` or `book review-input --section`.

Flat routes continue to use `sections` directly. A flat route included in a chaptered route
gets a chapter named for the included route. Named appendices follow main chapters.

## Choose the proof detail for the route

Keep the complete checked argument in its proof card. Use the route's agreed reader, prerequisites and proof
obligations to choose what the reader sees. A route can show its proof beside the claim, place it later or in an
appendix, or select an existing alternative. Use `proof: omit` for a cited input whose proof is outside the agreed
scope or for an explicitly requested statement-only view. Give readers the exact citation for a borrowed result
and identify the proof card or destination when the route defers a proof. Use glue to preview the idea and guide
readers to the proof. For a substantive change to a displayed proof, check that proof and its uses against the
exact claim. The [paper harness's reference proof](../../writing-harness/references/cards.md#fact-cards) serves a
similar purpose.

## Show levels

`book render --level`: L0 definitions, claims and conventions only (the statements of the book);
L1 adds examples; L2 adds proofs; L3 adds glue (lecture-note form); L4 adds exercises with
solutions. The cards are the same at every level. Labels come from the card's `label`, index
entries from `index`.
