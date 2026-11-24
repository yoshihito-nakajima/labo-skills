# Views, slices and queries

All views are generated from the cards and may be regenerated at any time.

## Reader-facing HTML

Use `book read --route R` for the page you give a reader. It follows the [paper reading layout](../../writing-harness/references/cards.md#reading-page) for the book's route. The page has a contents menu, readable paragraphs and transitions, adjustable type
size and width, light and dark themes, and folded proofs and solutions. The default output is
`output/book-R.html`. In the workspace that serves `output/` locally, give the reader its loopback URL.
The local bundle at `local/cache/mathjax/3.2.2/tex-svg-full.js` is embedded when available.
Use `--mathjax-bundle FILE` to choose another local MathJax SVG bundle. The self-contained
copy supports touch selection, comment export, and a control to expand all proofs.

The book supplies the displayed kind and number of each target. Compare HTML and PDF
from the same route when handing off both. Where a project uses custom PDF counters, compare with
those actual numbers. Check a section link, a typed reference, a folded proof and a selection
comment on the first assembled preview. Later check the changed content and affected controls.
Comments carry the selected text, the source card and the reading version. In a folded proof,
the comment points to the proof card. Apply reader-text corrections to the cards and regenerate.

## Card and dependency tools

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
