# Views, slices and queries

All views are generated from the cards and may be regenerated at any time.

- `book graph --route R` writes `route/R/dependencies.yaml` in schema v1 of
  [knowledge-dependencies](../../knowledge-dependencies/SKILL.md): nodes are the route's
  definitions, claims, examples, exercises and conventions; a node requires what its statement
  and its chosen proof require; borrowed cards are `external`. Check it with
  `dependencies check`, `order`, `closure`, `impact`. One graph is one route with one choice of
  proofs; alternatives are separate routes.
- `book closure ID...` / `book impact ID...` work on the whole root, across books.
- `book html --route R [--slice S] --name N` writes one static page to `output/N.html`
  (`--out PATH` elsewhere). Cards in reading order with status colors, STALE marks, links
  between uses, search, a kind filter, and a layered dependency graph with two granularities
  (cards, sections). Clicking a node highlights its prerequisites or its dependents.
  It is a local reading aid: in a workspace that serves `output/` on the loopback address it is
  visible only on that machine, and it is not a publication.
- Slices: `closure:<id>` (what the card needs), `impact:<id>` (what depends on it),
  `section:<n>`, `area:<name>`, `kinds:A1,A2`.

## Questions that are queries

| Question | How |
|---|---|
| What does this result need? | `closure` |
| What must be reread after this change? | `impact` (prerequisites changed → dependents and anchored prose) |
| Which statements does the book make? | `render --level L0` |
| Is the volume complete? | `status --route R`: all C2 OK, no open major finding, no error |
| Where do two books differ? | compare their routes' card sets and chosen proofs (both are lists of ids) |
| Which claims have two proofs? | A3 cards sharing `proves` |
| What does book B borrow from A? | the `borrows` of its entrance cards |

Cross-book questions treat each route's sequence as a list of ids over the shared pool; a
union or difference of two routes is set arithmetic on those lists. Ask for it by id lists
before building anything more.
