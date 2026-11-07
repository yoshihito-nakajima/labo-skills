# Plan format

Keep the plan in the project (for example `reading/<slug>/PLAN.md`). Fictional
example values below.

## 1. Weight table

| Source unit | Pages | Role mix | Why this weight |
|---|---|---|---|
| §2 Background (pp. 3-5) | 7 | 1 opener, 4 definitions, 2 figure pages | needed to state what is preserved |
| §4.2.1 Method A (pp. 10-11) | 3 | overview, mathematical core, full code | the method the audience came for |

State the total, the assumed words per page, and what is deliberately light.

## 2. Transition table

| From → to | Done | Open | Answered next by | Link is |
|---|---|---|---|---|
| §3 → §4 | local and global methods each lack one property | a representation with both | embeddings | source (p. 9) |
| 4.2.1 → 4.2.2 | A needs dense O(n^3) matrices | a sparse alternative | Laplacian-based method | speaker's |

Subsection and section links are rows; slide-to-slide links are the closing
question of a page and the subtitle of the next.

## 2a. Section map

One entry per section, written before its pages:

| Field | Content |
|---|---|
| Before | what earlier sections settled; the limits this section takes up |
| Problem of the section | the one question |
| Subsection chain | each subsection with the limit of the previous one that it removes (an arrow chain or small graph); major / thin |
| After | what is handed to the next section; what stays open |
| Source position | section, subsections, pages |

The section's opener page is built from this entry.

## 2c. Root list

When a detailed reading note exists, take the roots and cards from its section map
([reading structure](../../reading-reference/references/reading-structure.md#background-card-and-shared-roots))
instead of deriving them again. One page near the front of the plan, listing the root problems the source returns to: an ID
(R0, R1, ...), its one-line statement, its shared example, and the subsections that come back to it.
The fields of the motivation card below follow [roots and lenses](../../reading-reference/references/roots-and-lenses.md);
each of the shared, lens, applied, specific and limit fields carries one named source
(a work and its figure or page, the speaker's reading, AI-created, or not applicable), as
in its [card data](../../reading-reference/references/roots-and-lenses.md#card-data). A field
whose source is the speaker's reading after a recorded search goes into the page's
"Open items" as well, so the talk does not present it as a sourced fact.
A section opener may show a method-by-lens table that the section's summary completes. Each
subsection's opening page names its root, so that different methods that answer the same
root read as one story. Roots come from the source's own statements of its problems; a
root the source does not state is marked as the speaker's reading.

## 2b. Motivation card

One card per concept the talk introduces. Major concepts get the full chain on separate
pages; minor ones get a thin version (problem in the subtitle, a small failure example).

| Field | Content | Origin |
|---|---|---|
| Used here | what this subsection's opening page uses: the question on the running example, the inherited result or obstacle, the figures, formulas and published application (each with its origin) | |
| Root | the root problem (ID from the root list, 2c) and the other subsections that share it | |
| Shared example | the root's common example (same figure on every subsection of the root) | |
| Lens | what this method attends to, its strength and weakness | source / cited original / speaker's reading |
| Applied view | this method on the shared example | |
| Specific example | where the lens is most visible, and why | |
| Limit example | the stated failure; it opens the next subsection | |
| Problem | what we want, with a concrete case | source / cited original / background |
| Why the previous tool is not enough | how the previous method fails on that case | |
| Idea and definition | the one-sentence idea (what is replaced in what), then the definition; why this and not an obvious alternative | |
| Actual computation | the algorithm or code as published | |
| What it achieves | what the computation gives, shown on an example | |
| Limit and next | what remains; it becomes the next concept's problem | |

**Page order of the chain (the one authority; other files link here):** the opening
page (used here, then the root, then the question on the running example), why the
previous tool is not enough, idea and definition, computation, what it achieves, limit and
next. The computation and its code go on one page when they fit: the algorithm's steps
on the left, each with its reason and source, the code on the right, and each code mark
pointing to a step number; split into two pages only when the text-size rule would be
broken (as a guide, more than about five steps or fifteen lines), and keep the marks
pointing to the step numbers. The computation covers
what it keeps, what fixes the obstacle, what has another aim and what limit remains (role map below). Each page's closing
bar is the question the next page answers.

**Role map** (for a method or algorithm; omit roles that do not occur): for each step or
group of code lines, `fix` (overcomes the obstacle of this subsection; name it), `aim` (changed for another intended purpose;
state the purpose), `inherited` (kept from the previous method; say what that means), `forward` (a limit that
leads to the next subsection) or `tidy` (bookkeeping, not emphasized). Check each assignment against the source or code.
See [roles](../../deck-from-references/references/inherit-new-forward.md).

**Reasons are sourced, never invented.** The reason a method exists (why this idea, why this
criterion) is taken, in this order, from the source being introduced, then from the original
papers it cites; quote the passage and give its locator (person, publication, title, page).
If neither states a reason, write "no stated reason" and either omit the claim or present
only an elementary computation labelled as such (for example, an eigenfunction calculation);
a purpose inferred from code or a result is labelled "speaker's reading". Never supply a
motivation from memory or plausibility.

**Origin tags** (one per field): `survey p.N` (the source being introduced), `cited:
Author, Publication, "Title", p.N` (an original paper the source cites), `background:
Author, Publication, "Title"` (standard material added by the speaker). A field without
a checkable origin is marked unverified in the plan and is not put on a slide as fact.

**Citation form** for figures, code and algorithms: person(s), publication (venue, year,
page or figure), title. Fictional example: `Example Author, Example Journal (2020),
"An Example Method", Fig. 1, p.3`. Code: author(s), repository
and file, line range, commit, license status.

## 3. Per-slide spec

One entry per page, in source order:

- **n. [role] Title**: the top line (a claim or a question, one line).
- **Paper passage** (required): where in the paper the claim of this page is made (section, paragraph, page). The default
  order of pages is the paper's order.
- **Arrangement** (a mock-up by the user, when given, is the arrangement): the parts of the page (columns, bands, a concept diagram), what each holds, in which direction, and what
  ties each part to the next: what each arrow or position means, in words the audience can say (one or two lines; for
  example "left: what goes in, middle: what comes out, right: a real use of it; the arrow means 'the method turns this into
  that'; the concept diagram under the right figure is the order the paper states, and it appears as the figure's shape").
- **What each figure shows and does not show**: for each figure on the page, what can be read from it (shape, colours,
  marks, caption) and what cannot; the words beside it use only the first, and the script's sentences about the figure rest
  on it. For a concept diagram: what it draws and the passage of the paper's text it comes from. Mark a supplementary
  experiment or a picture made for the talk, and who produced it.
- **Key** (for a page that shows a figure): what the figure's colour, size or marks mean, in one line of plain words, and
  the word that must be defined on this page.
- **Marks** (for a page that shows a figure): for each mark on the figure, where it is and what actually happens there.
- **Panels** (for a page about a figure): the panels shown and the panels not shown (said in a sentence, or left to the
  appendix). A figure may be shown by a few panels, but every main-text figure has at least one page.
- **Method property** (for a result page): the one word for what this figure shows about the method, and the steps of the
  code map that act (they are lit in the small code-map recap on the page).
- **Script**, written before the page's words: it walks through the page's elements in reading order, about one short
  sentence each, says how they tie together and gives the reason; nothing at length on what the page does not show; no
  claim the passage and the companion units do not carry ([the script and the words on the page](page-words.md)).
  Each sentence is marked *page* or *spoken*. **Sentence-to-element table** (instead of a list of the page's
  lines): for each *page* sentence, what it refers to, the element that shows it, and the words on the page
  ([procedure](page-words.md)).
- **Top line, bottom line, next question**: full short sentences, subject and verb written out; the top line is the claim,
  the bottom line what was established and why it matters, the question is answered by the next page's top line.
- **Evidence figures**: a figure of a later part shown as evidence for a claim of that passage (marked "根拠" on the page,
  outside the figure order); allowed only if the passage states the claim the figure supports. Evidence is a contrast: the
  existing method and the paper's method on the same input, side by side. List its reads: the mark, what is seen
  there, and which point of the passage it shows, each with its source (the companion's read or the note's page).
- **Example figures**: a page that shows a figure of the paper only as an illustration (not explaining it) lists it as an
  example; the words around it say what it lets one read, and whether the method got it right is left to the page that
  explains it, which is named here and shows the other panels.
- **Unit** (when a companion exists): the companion units the page comes from (`fig2:difference`, `lineage:<name>`, ...), and
  where the page sits: main body, or appendix with its label (a main page names the appendix page it points to).
- **Locator**: source section, subsection and pages (shown on the page as a tag),
  equation, figure, algorithm numbers.
- **Concept role** (for a concept chain): one of the chain's pages named above
  (problem, why the previous tool is not enough, idea, computation, achieved, limit).
- **Subtitle** (when the style has one, as the reading deck does): the premise carried over from the previous page.
- **Body**: at most about eight lines or the equivalent in formulas; name the
  formulas, the figure or the code shown.
- **Code**: file, function, line range (from `extract_code.py`), who wrote it, runs or
  not and how checked, and the lines to look at with what is characteristic there.
  No line count in the title.
- **Stage view** (when a presentation deck is wanted): the pipeline or picture that
  page becomes (input, operation, output) and which reading pages it merges; no claim
  that the page itself does not carry. See [two decks](../../deck-from-references/references/two-decks.md).
- **Symbols introduced**: each new symbol in backticks with its definition and source,
  separated by semicolons (`` `L` = D - W (survey p.11); `W` = neighbor weights (p.7) ``).
- **Symbols used**: every symbol the page shows, in backticks. A symbol the audience
  already knows is listed once before the first page as `**Assumed known**: ...`.
  `scripts/plan_symbols.py PLAN.md` must report no symbol used before or without its
  introduction, and no forward reference, before the deck is built.
- **Note pages** (when a detailed reading note exists): the note's section, equation or figure
  labels this page comes from (they become `\noteref{...}` on the deck page), or "none" with the
  reason (deck-only material, which is then added to the note first). See
  [two decks](../../deck-from-references/references/two-decks.md#link-to-the-detailed-note).
- **Understanding check** (plan only, not shown on the slide): one question the speaker should be
  able to answer after this page, and where in the note the answer is. It is the handle for
  rehearsal, anticipated questions and a question-answering helper.
- **Open items**: anything unverified on this page.

## 4. Open decisions and unverified items

List each with a recommended default and the page it affects. Misprints or
inconsistencies found in the source belong here with their locators.
