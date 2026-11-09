# Section-structured page (survey papers)

For a paper read section by section (see the
[survey profile](../../../reading-reference/references/survey-profile.md)). It replaces the
figure-spine order of [companion-ideal](companion-ideal.md) when figures are many but not the
only spine; for a figure-centred paper keep that order and add only the section head panel.

## Layout: five folds, any number open at once, any number open at once

Top level, in the order the reader uses them. These are folds, not exclusive tabs: several can be open together so the reader can read in one and check in another.

1. **Reading** (open at first) — the whole paper read once without preconceptions. It is **folded per top-level section** (the first fold open, the others closed; the fold's heading shows only title and pages, never the summary); subsections are not folded and run on inside their section; a paper without nested sections gets one fold per section. Per section, in paper order: the **original** (the section's page region as one image, page breaks marked) on the left and the **faithful translation** on the right, side by side; then, only **after** them, a short **what this section says** line (question → answer, one or two lines). The section's entrance, selling point, weights and bridge are not shown here, so nothing is told before it is read. The same original image is used again in the Deep dive (reuse the image, do not store it twice). A section that is only a heading (its text starts in a subsection) shows the heading line and a note, with no original frame. After the last section comes the **whole picture**: what the paper learns and how, each chapter's question → answer, and the bridge from chapter to chapter, so the connections between chapters are read only after all sections have been read. The end of each section links to its deep dive, figures and code, which are not reproduced here.
2. **Figure flow** — one card per figure, in the paper's page order (check this order against the source PDF; do not assume figure-number order is page order). No map or summary line on top: the flow is the sequence of cards itself. A card, in this order: **what it follows from** (the record's links to earlier figures, written "From Fig.X: relation, what stays and what changes"; omitted for a figure that starts a line), the **original figure** (for a table or figure without an image, crop the page region of the source), **what to look at and how to read it**, **colours**, **terms needed to read the figure** (term, what it is and what it is good for, and its **basis** — the paper's caption or text, or "AI lookup, unchecked"; keep the reading faithful to the caption and mark every addition), and last the **sections where it occurs** (links to the deep dive). Interactive units stay in the appendix figure list, linked from the card. The figure-flow fold is self-sufficient: from it alone the reader sees the order of the figures, what each shows and how they connect.
3. **Code flow** — a separate fold: the sections that have code in paper order, with the main code, the goal in one sentence, and the code sections it receives from and hands to; each row links back to its section.
4. **Deep dive** — the sections, nested as in the paper, each folded. Inside a section the order is the order of study: what it says → entrance → head panel → original and translation → figures (what to look at, colours, how it differs from neighbours — written once here so the reader need not look it up again) → code (whole code, then annotated, then comparison) → terms → ledger → explanation and older units.
5. **Appendix** — figure list (with the figure units), code list, whole ledger, materials, acquisition state, request list. These are indexes; the reading order does not depend on them.

Both reader types enter the same way; the weights decide only what the reader opens first. A figure's colour legend and a code's reading belong to the section where they occur, not only to an index.

## Section unit (same order in every section)

0. **What this section says** (one or two lines: question → answer; in Deep dive it comes first, in Reading it comes after the translation) and **entrance** (a visible paragraph, not folded): what the previous sections gave, what is still missing, what this section does. A matching **bridge** closes the section and says what is handed on.
1. **Head panel**: position; question, answer, evidence; selling point; what it receives and
   hands on; its figures with colour legends; its code with kind and state; its materials.
2. **Original and translation**: the original passage and the faithful translation side by side.
3. **Figures** of the section (static copy with caption, colour legend, links to other figures; the
   interactive unit stays in the figure list, with a link — one interactive component per figure).
4. **Code**: a foldable goal block (what the code does as a whole and why this tool); then **the whole code with nothing added** (one heading per Step, open); then the **annotated version** (folded): Steps whose code carries a note directly above every line, with the comparison counterpart on the line, the specification of the functions each Step calls, math correspondence after each Step, the meaning of the result, then the comparison card ([comparison](comparison.md)).
5. **Terms** of the section (see below), then the **math ledger of the section** (concepts and claims in full, with proofs) — the overall ledger stays in the appendix; the head of the section lists its concepts with a one-line gist each; see the next part.
6. **Explanation**: the long explanation of the note's PDF unit, converted to HTML from the same TeX, so both outputs carry the same length; older units last.

## Original and translation

- Show the original **as the page region of the section** — from its heading to the next heading
  (located from word positions of the PDF text layer), not whole pages; embed the image directly
  (no lazy loading that depends on script events). When the heading cannot be located, show whole
  pages and say so.
- **One region, one place.** When the section runs across pages, join the per-page crops into a single
  continuous image (page breaks marked by a thin dotted line and a small page label; header and page number
  trimmed away) with one caption giving the page range. Do not list one figure per page: a paragraph or
  formula that crosses the break must read as one. Show it in a scroll area of about 85% of the screen height so that the original and the
  translation can be read side by side, with a button that expands it. Stitching needs Pillow; without it the builder
  shows the pages separately and says so.
- Faithful translation is shown without commentary; reader's notes go in a separate collapsed
  block labelled as not the paper's statements. A heading with no body says so.
- Check coverage: compare the translation length with the original's per section and read any
  short section against its pages; coverage is not assumed from the file being present.

## Navigation

Hash links open every ancestor block. "Open all / close all" is provided. Each section's summary
line shows title, pages, weights, code kinds and its selling point, so the closed page is a list.

## Record format and builder

`assets/section-record/example.json` is a fictional record: sections with question, answer,
evidence, selling point, weights, figures, code (kind, state, source, licence, file), materials;
section-level `steps` and `comparison` (rows with status same / changed / only_left / only_right,
left and right as `[file, first, last]`, `null` or `{"lit": "..."}`) or `no_comparison_reason`;
a `figures` table with `color_checked`; `edges` as `[from, to, what]`; optional `figure_links`.

- `scripts/check_section_record.py RECORD.json` — run first; fix errors before building.
- `scripts/build_section_page.py RECORD.json --out DIR [--original PDF]` — writes `DIR/index.html`
  (collapsed hierarchy, one file), `DIR/panels/p<ID>.tex`, `DIR/codecards/c<ID>.tex`. With `--original` and a
  `heading_word` per section it embeds the original page region beside the translation.
  `\input` the panels after each section heading and the card after the section's explanation in the TeX note;
  the same record then drives both outputs. The ledger and appendix are attached as HTML in the record
  (`ledger_html`, `appendix_html`) or generated by a project-specific step.

## Concepts in the ledger: say it where it is used

A ledger entry that gives only the formal definition forces the reader to know already what the
object is for. Each concept record carries three parts, read in this order:

- `gist` (one or two lines): what it is and what it is good for in this paper.
- `explain` (a short paragraph, not a copy of the paper): the definition in other words, the
  intuition, its role in the method, where it appears in the code or figures, what it is often
  confused with. Mark anything beyond the source and standard definitions as the writer's addition.
- `definition`: the precise statement.

A reference to a concept (in a claim, a section head, a Step, a figure note) never appears as an id alone:
write the name and the gist beside it, so that no one has to open the appendix to follow the sentence. The appendix
link remains for readers who want the full entry. The head of each section lists its concepts as name plus gist.
Glossary terms of the mathematical kind get one or two lines (what it is, what it is good for); a bare
paraphrase of the name is a defect. `check_section_record.py` rejects a concept without these parts and warns
when `explain` repeats `definition`, when a gist exceeds two lines, or when a glossary entry is shorter than its name needs;
the builder expands references automatically (`concepts`, `claims` in the record).

### Two ledgers, linked both ways, folded

The section ledger and the appendix ledger describe the same entries and must reach each other in one click.
Fixed id scheme: section concept `sc-<id>`, section claim `ss-<id>`, appendix concept `a-<id>`, appendix claim `as-<id>`.
Every entry ends with a link to its twin; every concept lists the claims that use it (linking to the claim's section entry);
every claim lists its concepts (linking within the same ledger); the section head's concept list links to the
section entries. Each concept belongs to one home section (`concepts` of that section) — a concept in no section
cannot be linked, and the checker rejects it.

Folding: the appendix ledger is folded as a whole (concepts, claims) and entry by entry; the section ledger is folded entry by entry.
The folded line always shows the id, the name and the gist (for a claim, its statement), so the ledger is readable
without opening anything; each ledger has "open all / close all". Hash links open every ancestor block, also on first load.
The builder's `ledger_auto_html` and `appendix_ledger_html` do this from the record; a project that builds its own ledger keeps the same ids and folding.

## Writing for a reader who knows the definitions but not the code or the field

No length quotas: write as long as it takes to carry the connection, the colours and what each term
does. A one-line item that only names a thing is a defect, not a summary.

- **Entrance and bridge**: say what was established, what is missing, how this section answers it,
  and what it hands on, in sentences. Edges in the head panel name the objects passed; the paragraphs
  say why they matter.
- **Figures**: what to look at, panel by panel, what each colour means (from the image and caption),
  how it differs from the neighbouring figures, and what the figure is evidence for.
- **Terms**: each term gets a plain explanation *and what it is good for* ("a ridge gives a centre line that
  survives noise"), where it appears, and its field. Terms the reader's mathematics already covers stay
  short; spend words on code, statistics, computing and the application field.
- **Code**: opening the code shows first a foldable **goal** block: what the code does as a whole
  and why this function, method or way of writing it is used rather than another (`flow` and `why` in the
  record), at the length and explanatory level of the links between sections. Then **the whole code with nothing added**: one heading per Step and the verbatim lines, shown open, so a reader can take in the shape before any commentary. Directly after it, the **annotated version** (folded in HTML): the Steps below. **Inside
  each Step the explanation lives in the code, not in a separate table**: every line has a note directly
  above it saying what it does, which symbol or formula of the source it is, and what trips a beginner
  (axis, shape, zero-based index, transpose, sign). Blank, import and closing-bracket lines may share a
  note with a neighbour. Where a comparison exists, the line also carries its counterpart on the other
  side — same / changed / only here, the counterpart's file and lines, and the reason — derived from the
  comparison rows, not written twice. A note must not restate the goal block. Notes are display only:
  the copy button and any saved file stay the verbatim original. Record form: per Step
  `lines: [[first, last, text], ...]` covering the Step's lines exactly once. Per
  library call, a specification card — name, the signature as used, what it returns (shape, order,
  conventions such as which factor a decomposition returns), cost, a short quotation of the installed
  version's documentation plus a summary in the note's own words. Take quotations from the installed
  version, not from memory; for software whose documentation cannot be reproduced, summarise and say so.
  After the Steps, what the result means and where it leads.
- TeX needs `amsmath, booktabs, array, longtable, listings, tcolorbox` (with the `breakable` library).
