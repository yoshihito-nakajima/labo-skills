# What `book check` reports

Each line is `CODE card-id: message`. **Errors** make the exit status 1 and block "complete"; **warnings** are real
signals that do not by themselves block. A warning is not to be silenced by editing the card until the check passes:
fix the cause.

## Structure and fields (errors)

| Code | Meaning and repair |
|---|---|
| `PARSE` | The file has no readable front matter or is not UTF-8 text. Fix the file. |
| `DUPLICATE-ID` | Two files carry the same `id`. Ids are unique across the root; merge or rename. |
| `ID-FILE` | `id` differs from the file name. Rename the file or use `book rename`. |
| `BAD-ID` | Ids are lowercase kebab-case starting with a letter. |
| `BAD-KIND` | `kind` is not a template code (A1–A6, B1–B5, C1, C2, D1). |
| `WRONG-PLACE` | The card is in a folder its kind does not use (fact cards in `pool/`, glue in `route/<slug>/card/`, ...). |
| `BAD-FIELD` | A front-matter field has the wrong type (a list written as text, ...). The value was ignored. |
| `NO-TITLE`, `NO-FIELD`, `NO-SECTION` | A required title, front-matter field or section is missing (not for `legacy` cards, which need `本文`). |
| `BAD-VARIANT`, `BAD-STATUS` | Value outside the allowed set (`unclassified` is accepted as a variant for imports). |
| `UNKNOWN-REF` | An id in `requires`, `references`, `proves`, `between`, `maps_to`, `borrows`, `relations`, an anchor, a `[[card]]` mention or a `[by:]` cite does not exist. |
| `DUP-REF`, `REQ-AND-REF`, `SELF-EDGE` | A list repeats an id; an id is both required and merely referenced; a card requires itself. |
| `CYCLE` | The hard prerequisites form a cycle. The message names it. Find the circular proof or the wrong edge. |

## Facts, proofs, relations

| Code | Meaning and repair |
|---|---|
| `NO-WELL-DEFINED` (error) | A recursive or quotient/choice definition needs `well_defined: [claim]`. |
| `PROVES-NON-CLAIM` (error) | An A3 `proves` something that is not an A2 claim (or an A1/A5 it supports). |
| `CITE-NOT-REQUIRED` (error) | A proof step cites `[by: x]` but `x` is not in `requires`. |
| `UNUSED-REQUIRES` (warning) | `requires` lists a card no step cites. Cite it or drop it. |
| `SHAPE` (error) | The proof lacks what its variant needs (both directions, base and step, existence and uniqueness, two inclusions). |
| `PROOF-SHAPE` (warning) | An `equivalence` or `unique-existence` claim whose chosen proof has another shape. |
| `NO-PROOF`, `NO-OWNER` (warning) | A claim past `stated` without a proof card; several proofs and none marked `owner`. |
| `TWO-OWNERS` (error) | More than one owning proof for a claim; mark the others `owner: false`. |
| `BAD-RELATION`, `RELATION-DIFF` (error) | Relation type not allowed; a `variant` relation or mapping without `diff`. |
| `NOT-CONVENTION` (error) | `conventions:` names a card that is not an A6. |
| `PLACEHOLDER` (warning) | A section still says `TODO`. |
| `UNKNOWN-SECTION` (warning) | A heading the template does not have. |

## Glue and routes (with `--route`)

| Code | Meaning and repair |
|---|---|
| `FORWARD` (error) | A card needs one that comes later in the route. Reorder, or preview it (B3) and keep the proof later. |
| `UNLISTED-BORROW` (error) | A card needs one that is neither in the route nor listed in an entrance card's `borrows`. |
| `BORROW-IN-ROUTE` (warning) | A borrowed card also appears in the route. |
| `ROUTE-UNKNOWN` (error) | The route lists an unknown card. |
| `DUPLICATE-IN-ROUTE` (warning) | A card appears twice, usually `proof_of` for a claim whose proof already follows it. |
| `REF-OUTSIDE-ROUTE` (warning) | Text cites `[[x]]`, which is neither in the route nor borrowed. |
| `BAD-BETWEEN` (error), `NO-ANCHOR` (warning), `TRANSITION-PLACE` (warning) | A transition must name exactly two neighbours, anchor both, and sit between them. |
| `PREVIEW-REQUIRED` (error), `PREVIEW-EARLIER`, `PREVIEW-MISSING` (warning) | A previewed result may not be a prerequisite; it should come later in the route and exist. |
| `OPEN-QUESTION` (warning) | A motivation card without an answering card in the route. |
| `UNUSED-GLUE` (warning) | Glue of this route that the route does not place. |

## Freshness, imports, reviews, mappings

| Code | Meaning and repair |
|---|---|
| `STALE` (warning) | A card an anchor points at changed. Reread, then `book anchor`. |
| `STALE-REVIEW` (warning) | Status `independent` but no recorded review matches the current fingerprint. Review again or lower the status. |
| `LEGACY`, `BODY-LEFT`, `UNCLASSIFIED-VARIANT` (warning) | Imported text not yet split; the old `本文` left in a card that says `legacy: false`; a variant still `unclassified`. |
| `NO-EDITION` (warning) | A source record without `edition:` or `sha256:` in its front matter. |
| `BAD-ADOPTION`, `BAD-AUDIT` (error) | Value outside `adopted/partial/not-adopted/outlook`, `TODO/OK/PARTIAL/MISSING/OUT`. |
| `NO-REASON` (error) | A partial, not-adopted, outlook or OUT row, or a resolved finding, without its reason. |
| `NO-MAP` (error) | A mapping row marked `OK` that maps to no card. |
| `NOT-SOURCE` (error) | A mapping row's `sources` names a card that is not a C1. |
| `AUDIT-STALE`, `AUDIT-UNPROVED` (warning) | A row marked `OK` whose target changed since, or is only `stated`. |
| `FINDING-TARGET-CHANGED` (warning) | The card a finding is about changed since the finding. |
| `BAD-SEVERITY`, `BAD-FINDING-STATUS` (error) | Value outside `major/minor`, `fixed/resolved-with-reason/open`. |
