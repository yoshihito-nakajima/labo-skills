# Reading a figure: the figure carries the background and the hand-off

A figure is on a page to be **read**, and what is read from it is the background of the
method that follows. A page that only says what the marks are, or only credits the source,
has not used the figure. The design is the same as for code pages
([code pages](code-pages.md)): numbered marks on the object, and a list that says what to see and
what it tells.

**Use it flexibly.** The full ladder fits a figure that shows a problem (a background figure, a limit
example, a failure of the earlier method, and every figure marked as evidence, 根拠). Other figure pages (an output shown as an example, an input
and output side by side, a figure that carries a pipeline) use only the steps that apply, or none: their
words come from the script and say what the figure shows
([the script and the words on the page](../../paper-talk-planning/references/page-words.md)). The plan
says which steps a page uses. Flexible means fewer steps on the page, never a figure whose *learn* is missing
from the script.

## The reading ladder

For a figure that shows a problem, in this order, each step on the slide next to the figure:

1. **See** — the specific marks: "an outer and an inner turn lie side by side"; a mark number on
   the figure points to them.
2. **Learn** — what that tells about the problem, in one clause, introduced with an arrow:
   "yet far apart along the sheet: near in space is not near on the data". This is the
   background the audience takes away, and it is a claim, so it has a source or is marked.
3. **Trouble** — what the figure shows cannot be done or goes wrong with the tool so far
   ("困りごと"). It is the limit example of the card and the reason for the next page.
4. **Hand-off** — the closing bar names the method that answers the trouble.

Steps 1-2 repeat per mark (two or three marks per figure; more is a second page).
Step 3 once. Each figure page therefore answers: what do I look at, what do I learn from it,
what is hard, what comes next.

## Marks

- Draw numbered marks on top of the **unaltered** figure and say on the page that they are
  the presenter's overlay (the figure is not modified). In the Beamer style:
  `\figmarked{width=...}{file}{\fmk{x}{y}{1}...}` with `x,y` in 0-1 of the image, and
  `\readitem{n}{see}{learn}`, `\readtrouble{...}`.
- Place a mark only after viewing the figure at a size where its parts can be told apart.
  Never describe or place marks from another paper's caption, from memory, or for an unseen figure.
- Prefer the feature that matters for the story (a pair of points, a path, a hole, a failure),
  not a tour of every panel. Name the panel when the figure has several: "left / right" if it
  has no letters.

## Card field

The note's card for a unit lists its figures, so that the page can be built from it.
The following uses fictional placeholders:

```json
"figures": [{
  "file": "figure_a", "source": "Example Author, Example Work (2020), Fig.1, p.3, cropped",
  "reads": [{"mark": "1 2", "see": "...", "learn": "...", "source": "locator | speaker's reading"}],
  "trouble": {"text": "...", "source": "..."},
  "leads_to": "next unit"
}]
```

A `learn` that rests on the writer's reading needs a recorded search like any card field
([roots and lenses](../../reading-reference/references/roots-and-lenses.md)). `trouble` is the
unit's limit example. A unit whose figure has no `reads` is not ready.

## Also required on every figure page

- **Legible**: labels the audience must read are legible at slide size; otherwise enlarge,
  or retype what is needed and link the crop.
- **Provenance, three-valued**: person, publication, title, page, and exactly one of
  "cropped, unaltered", "redrawn", "AI-created". A figure borrowed from a paper on another topic says what it
  is borrowed to show.
- **Symbols**: every symbol used in the reading is defined on the page or on the page it points to.
- **Not shown, not cited**: no bullet leans on a figure that is not on a slide.

## Checks

On every figure page: a mark that does not point at what is said (view the page), unreadable labels,
provenance not stated, words beside the figure that it cannot show, and overlaps (`deck_audit.py
--overlaps`). On a page that uses the ladder, also: no see (marks not stated), no learn (the figure
teaches nothing the next page uses), no trouble, no hand-off; such a frame has `\figmarked`, at least one
`\readitem` and one `\readtrouble`. Cut the least necessary clause rather than shrinking text.
