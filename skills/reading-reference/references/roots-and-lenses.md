# Roots, lenses and the background of each method

Several methods in a paper often answer the same problem, yet each looks at it through
a different property and is good at different things. Their backgrounds therefore share
a root but not their pictures. This file is the one place that defines how such
backgrounds are found, recorded and shown; reading notes, talk plans and decks link here.

## Three layers and three views

Every method's background has three layers:

1. **Root** — the shared question (for example: recover a common representation
   from partial observations). The same for every method under the root.
2. **Shared example** — one dataset or figure applied to every method under the root
   (for example a survey figure that runs all methods on the same input). The same for
   every method: it is the yardstick on which their differences become visible.
3. **Lens** — the property of the problem this method attends to (for example,
   sensitivity to missing observations or computational cost), with what it is good
   and bad at. Different for every method.

Because the lens differs, each method shows three views:

- **Applied view** — this method on the shared example: what it gains and what it loses
  on the common yardstick.
- **Specific example** — data on which this lens is most visible (often from the
  method's own proposal or an application paper). It differs between methods by design.
- **Limit example** — where this lens fails, as stated by a source; it becomes the
  background of the next method.

So a method A is introduced by *shared background + A applied + A's specific example*,
a method B by *shared background + B applied + B's specific example*; A's limit example
leads to B.

## Collect them while investigating the sources

When a reading note is first built from a paper and its literature, collect for every
method, alongside the method and application evidence of
[paper preparation](paper-preparation.md#method-understanding-with-literature-evidence)
and [applications to code](application-to-code.md#find-and-inspect-the-application-evidence):

- its lens and its strengths and weaknesses, each with the passage that states it
  (the paper, then the original papers it cites);
- a shared example for its root: prefer a figure in the paper that already compares the
  methods on one input;
- its specific example: the application in its proposal or in an application paper where
  the lens is visible, and why that example shows it;
- its limit example: the failure the sources describe.

A strength or weakness no source states is marked as the writer's reading. Do not create
an experiment (in particular an AI-created one) to stage a strength; prefer the sources'
own figures, and label any made figure under [R5a](source-rules.md).

## Let the card decide what to search

Reading the target paper from front to back and following its references is required
elsewhere ([R3](source-rules.md), [paper preparation](paper-preparation.md)). The card adds
*which* questions that search must answer. Work in this order:

1. Read the target paper and fill every card field it answers, with its locator.
2. List the open questions: each field the paper leaves empty, and each strength,
   weakness or limit that rests only on a passing sentence. Phrase each as a question
   ("which work shows where method A fails?", "where does this application example come from?").
3. Search for each question where its answer is likely to be written (table below),
   following named dependencies only, as R3 bounds the search.
4. Fill the field with the source found, or record the search (below) and only then
   use the writer's reading.
5. Fix the section map and write the unit only when its card is complete.

| Field | Look first in | Then in |
|---|---|---|
| lens, strength | the method's proposal (introduction, discussion); the target paper's comparisons | comparative studies; theoretical analyses (convergence, guarantees) |
| limit | the target paper's limitations; the proposal's discussion | later papers that diagnose the failure |
| shared example | the target paper's comparison figure | benchmark papers running several methods on one dataset |
| applied view | the panel of that comparison figure | the proposal's figure on the same data |
| specific example | the proposal's experiments | application papers ([applications to code](application-to-code.md#find-and-inspect-the-application-evidence)) |
| code | [R18](methods.md) | — |

`scripts/check_cards.py --todo` lists the open questions of a card file.

## Background card

Decide the card in the section map before the unit is written
([reading structure](reading-structure.md#fix-the-scope-and-the-section-map-before-editing)).
Fields, in this order:

1. **Used here** — the question this method asks, the result or obstacle inherited from
   the previous subsection, and the figures, formulas and application used, each with
   its source (person, publication, title, page).
2. **Root** — its ID and one line, and the other subsections under the same root.
3. **Shared example** — the root's common example and where it is shown.
4. **Lens** — the property this method attends to, its strength and weakness, with sources.
5. **Applied view** — this method on the shared example (figure and source).
6. **Specific example** — the example where the lens is visible, and why.
7. **Limit example** — the stated failure, and the subsection it leads to.

Keep a one-page list of roots near the front: ID, statement, shared example, and the
subsections that return to the root. When the material is generated, keep the cards and
the root list in one data file read by the generator, and make the generator refuse a
source unit with a missing field or an unknown root.

## Card data

When cards are kept as data (for a generator, or for a talk plan that reads them), use one
JSON file with this shape; `scripts/check_cards.py` checks it and derived tools read it.
The source names and locators in this example are fictional placeholders.

```json
{
  "roots": [
    {"id": "R1", "question": "...", "source": "Example Survey (2020), §2, pp.4-5",
     "shared_example": {"text": "...", "source": "Example Survey (2020), Fig.1, p.6"},
     "nodes": ["unit-a", "unit-b"]}
  ],
  "nodes": {
    "unit-a": {
      "uses": ["...", "..."],
      "roots": ["R1"],
      "shared":   {"text": "...", "source": "Example Survey (2020), Fig.1, p.6"},
      "lens":     {"text": "...", "source": "Example Survey (2020), p.7"},
      "applied":  {"text": "...", "source": "Example Survey (2020), Fig.1(a), p.6"},
      "specific": {"text": "...", "source": "Example Author (2021), Fig.2, p.8"},
      "limit":    {"text": "...", "source": "Example Survey (2020), p.7"},
      "code": "..."
    }
  }
}
```

Each of `shared`, `lens`, `applied`, `specific` and `limit` is a pair of text and source.
The source is exactly one of:

- a locator in a source: person or work, year, and figure, equation or page;
- `speaker's reading` (or `発表者の読み`) — the writer's own synthesis;
- `AI-created` (or `AI 作成`) — an example, figure or computation made by an AI;
- `n/a: <reason>` (or `該当なし：<理由>`) — the field does not apply to this unit.

A place inside the reading note itself ("the note's example", 詳細版の…) is not a source:
name the work the note took it from. Other keys may be present and are ignored.

A pair may carry `"searched"`: a list of the places checked for this field, each with an
outcome, using the same outcome words as R18 —
`{"where": "Author 2008, §5, p.7", "outcome": "states it" | "found, does not state it" | "inaccessible" | "not found in the searched scope"}`.
The source `speaker's reading` is accepted only with a non-empty `searched`: the writer's
reading comes after a recorded search, not instead of it.

## In derived views (talks)

A talk takes the cards from the note rather than re-deriving them
([plan format](../../paper-talk-planning/references/plan-format.md)). The opening page of
each subsection shows the shared background with the same figure as before, then this
method's applied view, then its specific example; the limit example opens the next
subsection ([transitions](../../deck-from-references/references/transitions.md)).
