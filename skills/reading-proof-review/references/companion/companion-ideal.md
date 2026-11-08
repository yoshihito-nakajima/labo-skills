# Ideal and page layout

## Purpose

The companion prepares the reader to present a method paper. After it, the reader understands
the main text and can present each main-text figure: what it claims, how to read it, which code
produces it, what is the same as and what differs from the earlier method, and what it does not
show. A presentation of a paper is largely a presentation of its figures, so the figures are the
spine.

The reader can follow mathematics and code but lacks the domain background. The page is read
before the detailed reading note and leads into it. The note stays the source of truth: every
explanation, picture and example on the page is taken from the note or computed with code and
labelled, and every unit points back to the note's section and page.

## Fix the story first (optional storyline layer)

Before any unit is written, `companion.json` carries the story in a few fields, checked by
`scripts/check_outline.py`: the shared introduction (`background`), the method map (`overview`) and
`difficulties` — numbered obstacles, each saying *why the obvious route or the earlier method fails*,
not only what is hard. Each overview step gives `why` it is needed here and `answers`, the ids of the
difficulties it answers (or `n/a: reason`). Every difficulty must be answered by some step, and every
step must answer one or say why not. The page shows each obstacle with the steps that answer it.

## What the reader can answer

For the paper as a whole:

0. **What the data are and what we want to see** — what is measured, why it comes in this form,
   and the change or structure the method should reveal, as a concrete picture.
1. **Where the method comes from** — the paper's Summary and Introduction in plain words: the
   obstacles it names and the novelties it declares; for each earlier work (family), what it was
   made for, what it does well, the weakness the paper names ("with this code, X is weak"), what
   the method keeps or changes, and what checking the source found. Lineages the code does not
   show (a concept, a neighbouring approach) belong here as reference; later developments are an
   optional, folded, sourced supplement.
2. **Where everything sits** — the main-text figures in order, each with its selling point and
   the code selling point it shows; the method's steps from input to output.

For every main-text figure, in the paper's order:

3. **What it claims** — the main-text sentence that cites it and the caption, with locators.
4. **How to read it** — each panel's axes, colours and sizes, and the marks to point at.
5. **Which code makes the point** — the step, the authors' functions and lines, the parameter
   values; the code selling point the figure demonstrates; and **where the figure's difference
   comes from**: the blocks of the whole code (steps and lines) that make the difference the
   figure shows, to the earlier method or between conditions.
6. **Same and different** — the earlier method's code beside the authors' code; for each
   corresponding block, what it does in plain words, where it comes from (inherited from which
   work, changed, added) and what the difference changes; coloured as the same, changed, or only
   in one.
7. **What behaviour to expect** — one run with controls on small synthetic data: the authors'
   and the earlier method's code on the same data and the same controls, so the reader sees what
   the code does when an argument moves. The paper's figure carries the claim; a remake on the
   paper's (or substitute) data, if any, is a folded reference.
8. **What to say and what will be asked** — the claim in a few sentences, what to point at, the
   questions a listener is likely to ask, what the figure does not show.
9. **Where to read more** — the note's section and page, the deck pages.

For every step of the method (supplement): the idea in words, terms, formula, a worked example,
and the code read from the first line, as in [step unit](feature-unit.md).

## Page layout

1. **Introduction (shared).** The picture (what is measured, why in this form, what one wants to
   see, with the paper's overview figure when it has one), the paper's question, the terms.
   Purpose and terms are stated once here and reused below. Then the **primer** (`background.primer`):
   what the method outputs, in plain words (`object`); that output taken apart, each part with its meaning
   (`parts`); what one can learn from it (`learn`); and every mark, size or colour the later figures use,
   with its meaning and the figures that use it (`encodings`). The reader can read every later figure
   from the primer alone; an encoding a figure uses that the primer does not introduce is a defect.
2. **Summary, Introduction and lineage** (taken from the note's
   [overview table](../../../reading-reference/references/lineage-and-comparison.md#overview-table)).
   The paper's Summary in plain words; the obstacles and novelties its Introduction declares; the
   families of earlier methods as the paper sorts them (good at, weak at, where compared); one card
   per earlier work: made for, the weakness, kept / changed by the method, what checking the
   source found, link to the note. Reference lineages (concepts, neighbouring approaches) are
   marked as such. Later developments, when added, fold below as an auxiliary list with sources.
   This comes before any code: the code comparisons later read as answers to these weaknesses.
3. **Correspondence table (the map).** One row per main-text figure, in order: the figure's
   selling point, the code selling point it shows (step, function), the earlier method, the
   reproduction level. Each row links to its figure unit and to the step units it uses. Below it,
   the method's steps from input to output.
4. **Main line: figure units**, Fig. 1 to the last figure, each as in [figure unit](figure-unit.md).
   A supplementary figure appears inside the figure unit that cites it, only when the main text
   needs it there for understanding.
5. **Supplement: the code from step 1.** It opens with the **code map**: the whole code of the
   method's entry function with each block coloured by the step it carries out (and the functions
   of other steps, such as scoring, that the entry function does not contain), so the reader sees
   "this part is step (i)". The reader meets it when starting to read the code continuously, not
   at the top of the page; figure units only link to its blocks. Then one
   [step unit](feature-unit.md) per step, in the order of the method. Figure units link into it;
   step units link back to the figures that rely on them.
6. **Sources used.** Every code repository (URL, commit, licence, files used), every dataset
   (source page, accession, hash, preprocessing, level), every paper figure (page and crop), and
   the open [request list](../../../reading-reference/references/resource-ledger.md#request-list).
7. **Parameter table, limits and glossary.** Every parameter (name, default, stated in the paper
   or code only, grid with the values added to show an effect, effect, code line); what the page
   does not show; every term with the unit that defines it.

## Qualities

- Words before symbols, symbols before code: a term is explained where it is first used, before
  it appears in a formula, a code excerpt or a control.
- One name per quantity: the text, the code notes and the controls use the same names; where the
  paper's symbol and the code's argument differ, they appear together.
- Nothing the reader must decode: reproduction levels are said in words with the data's name, panel
  names are the paper's, every run says whether it remakes a named panel or serves reading the
  code, and every preset shows its values.
- Background first and again just before the code: each unit opens with why the thing is needed;
  just before the authors' code it restates the purpose and idea.
- Concrete before general: a picture and a small numerical example come with every formula.
- The main line stays visible and supplements fold.
- The paper's figures are always explained, whatever could be run.
- History before code: the earlier methods' purposes and weaknesses are told before any code
  comparison, so each changed block reads as an answer to a named weakness.
- A comparison says what the code does: every corresponding block is explained in words (what it
  does, where it comes from, what the difference changes); the same / changed label only
  summarises that.
- One place to move per figure: controls live on one small synthetic run per figure, with the
  call shown once and the controls as its arguments; the claim itself is carried by the paper's
  figure. Nothing the reader moves takes longer than a moment to switch.
- A claim can be checked by hand: every "learn" of a figure either points to a control setting of
  that run (earlier method and the authors' method side by side, same data, same controls) or says
  that it rests on the paper only.
- Code verbatim; only parameter values vary, shown beside the code and bound to controls. The
  earlier method's code is shown in full beside or directly before the authors' code
  ([comparison](comparison.md)).
- One colour code for same / changed / only-in-one, used in both code panels, the correspondence
  list and the figures.
- Figures drawn with the paper's encoding, next to the paper's figure cut out of the source, with
  numbered marks linking the two.
- Every number and figure labelled by provenance and reproduction level; computation with the
  authors' code first ([fidelity](fidelity.md)).
- One self-contained HTML file, offline, small, private.
