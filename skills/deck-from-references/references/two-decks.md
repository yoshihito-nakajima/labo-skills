# Decks from one plan

## When a companion page exists: one source, two builds

When a [companion page](../../reading-companion/SKILL.md) of the paper exists, slides are taken from
it, not from the detailed note: the note holds far more than a talk can use, and a claim picked
from it by hand is where mistakes enter. The companion already holds the selected, sourced
material (the question, the lineage of earlier methods, each figure's claim, reading, difference
and presenter's notes, the code map, the checks). The chain stays short and checkable: slide →
companion unit → the note's section and page (carried by the companion's links) → the paper.
Audience, time, language and the number of slides are asked for each request and recorded in the
plan, never fixed here. The order of a paper introduction follows the paper from the front (see
[paper-talk-planning](../../paper-talk-planning/SKILL.md)); the figure rule below concerns the pages that explain figures.

**One source, two builds.** The talk is one body (the main part) and one appendix. Build
1. the **main deck**: body only, at speaking pace (the stage rules below: figure first, about 40 to 60
   words, the speech carries the reasoning);
2. the **deck with appendix**: body, then the appendix pages (denser pages that carry the
   reasoning on the page: the code of each step, the lineage cards, the parameter table, figure
   details, what was checked and not confirmed, likely questions, later developments).

Two thin roots (`main.tex` inputs the body; `full.tex` inputs the body, then the appendix) share every
page, so the pages correspond one to one. A main page points to its appendix page with `\appref{B3}`
and the appendix page carries `\applabel{B3}`; in the main deck the pointer is a small grey
tag, in the full deck it is where to turn. Nothing is on an appendix page that the companion does
not carry (add it to the companion first). The detailed note is opened only to settle a doubt about a
claim, through the links the companion shows.

**Page tags** (`assets/beamer/companionlink.sty`): every page has `\fromunit{ids}` naming the companion
units it comes from (`fig2`, `fig2:difference`, `lineage:<name>`, `step:<id>`, `codemap`, `summary`, ...)
or `\nounit{reason}`. `scripts/link_companion.py check BODY.tex --appendix APP.tex --companion companion.json`
reports a page with neither tag, an unknown unit, an appendix pointer without its page, and the figure rule:

**Result pages.** Each page about a figure shows the panels that carry the point of the method (the others are
named in the plan and in the appendix), ends with the one-word property of the method the figure shows (the
companion's `talk.property`), and carries a small recap of the whole-code map with the steps that act lit (the steps of
the figure's *difference*), so the code map seen once is seen again where it matters. The introduction has a reading primer page or
pages before the first result figure (the companion's `primer`).

**Figure rule.** The main-text figures are each explained in the body, and the pages that *explain* them appear in the
paper's order, Fig.1 to Fig.N ascending, even when the rest of the talk follows a story order. The
check fails on a missing figure or on pages out of order. A figure shown earlier only as an **example** (an
introduction that needs a real output) is not an explanation: the page lists it with `\asexample{...}`, marks it on the
page with `\exampletag` (a small "例" beside the figure label), and the page that later explains the figure
does not repeat the example panel but ties back to it ("the figure of page 1") and shows its other panels.

## When no companion exists: reading deck and stage deck

A paper-introduction talk usually needs two artifacts. They serve different people
at different moments, so they are built differently. Build the reading deck first;
derive the stage deck from it.

| | Reading deck (for understanding) | Stage deck (for presenting) |
|---|---|---|
| Reader | the speaker, or a reader alone, before and after the talk | the audience, once, at speaking pace |
| Unit of a page | a statement with its justification, scope and source | one transformation: what goes in, what is done, what comes out |
| Words per page | about 100 to 140 | about 40 to 60; the speech carries the reasoning |
| Where the reasoning is | on the page (definition, formula, caveat, locator) | in speech; the page shows the skeleton |
| How links are shown | grey subtitle (premise carried over) and a bottom bar (next question) | arrows between boxes on the page, a bold takeaway, one next question |
| Figures | next to the claim they support, with a reading block | the picture is the page; explanation is spoken or a short label |
| Source and caveats | a source tag and a scope sentence on every page | a small source tag; caveats move to speech or backup |
| Background | dark, text first | light, figure first |
| Failure to avoid | handout density projected on a screen | slogans without the formula or the source behind them |

## Rules for deriving the stage deck

0. **Chains and sources carry over.** The concept chain ([order in plan format](../../paper-talk-planning/references/plan-format.md)) and the roles (kept, fixes the obstacle, other aim, tidy, limit), the origin tags and the credits are the same in both decks; the stage deck may thin a chain but not drop its problem or its payoff.
1. **No new claims.** Every stage page cites the reading page(s) it comes from
   (a comment in the source and a line in the plan). If a claim is not in the
   reading deck, add it there first and verify it.
2. **Keep the same order and the same links.** The reading deck's closing question
   becomes the stage page's next question; the reading deck's subtitle becomes the
   spoken bridge.
3. **Pipeline pages for methods.** Show input, operation (the key formula), output as
   boxes joined by arrows; the selling point is a red label, not a paragraph. The
   code page follows, shared with the reading deck ([code pages](code-pages.md)), and
   the pipeline names the lines that implement each box.
4. **Figures first.** Reproduce the source's figure (or a faithful schematic,
   labelled as such) and add a one-line reading, not a block.
5. **One idea per page, but not one fragment per page.** Merge reading pages that
   share one picture; split only when a page would exceed the density.
6. **Both decks, both languages, one source of claims.** A change of a claim is made
   in the reading deck and propagated.

## When to build which

Build the reading deck when the user wants to understand, to decide what goes on the
slides, or to check the plan. Build the stage deck when the user will present. If
only one is requested, build that one and say that the other can be derived.

## Link to the detailed note

When a detailed reading note exists, the reading deck is a way into it, and a page is only
understood when the reader can go from the page to the note's full account. So:

1. **Every reading-deck page names where it comes from in the note**, as a section, equation or figure
   label with its printed number and PDF page, as a link to that page: "Detailed note §11.4 (p.89)".
   A page with no counterpart says so (`\nonote{reason}`), and its content is added to the note first
   (rule 1 above: no new claims in the deck).
2. **Use stable labels, not typed numbers.** The note gives each unit a `\label`; the page cites the
   label with `\noteref{sec:key,eq:key}` (`assets/beamer/notelink.sty`). `scripts/link_note.py build`
   reads the note's `.aux` and writes the number and page of every label, so the links follow the
   note's last build; rebuild the note, run `build`, then build the deck. Put `\noteref` before the
   page's source tag and append `\notetag` to the tag.
3. **Check**: `scripts/link_note.py check <deck sources> --aux <note .aux>` reports a page with neither
   `\noteref` nor `\nonote`, and a label the note does not have.
4. **Reverse table**: `scripts/link_note.py reverse` writes a list for the note's appendix, from each
   note label to the deck pages that use it, so the reader can also go from the note to the deck.
5. The stage deck cites reading-deck pages; it reaches the note through them (stage page → reading
   page → note).
