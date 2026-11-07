# Design rules: how the page looks

These rules fix crowded, small, uneven and overlapping pages. Check them on the render. What the words say
(the script, the top and bottom lines, keys, concept diagrams, evidence, examples) is set in
[the script and the words on the page](../../paper-talk-planning/references/page-words.md); this file says
how they are set on the page. Fictional examples.

## Length and size

- **Length is the constraint; calibrate it against the user's own example deck.** Measure the example
  (`deck_audit.py example.pdf`): median and maximum words per page, median body word height over page width,
  and write the numbers into the project's style card. `deck_audit.py deck.pdf --example example.pdf`
  reports pages above 1.2 times the example's maximum words (the usual sign that a page is not in the user's
  manner; count the words of source lines too) and notes pages whose text size differs from the example's.
  A page that is too heavy loses or moves material, or is split; text is never shrunk to make it fit.
- **A mock-up drawn by the user is the layout.** When the user gives one, its arrangement, sizes and amount of text
  are followed, and they override the rules of this file; differences are reported, not "corrected".
- **Sizes by role, as defaults.** The style sets one size per role (title, label, explain, caption, figlabel,
  cite, note, closing, nextq) with `\setflowsize{role}{pt}{leading}`, from the example's ratio. A page may
  change a role's size when it has room or needs it: a `\setflowsize` inside the frame stays local to that
  page, so no `\fontsize` is written by hand. Sizes may differ between pages; the length may not grow.
  `--previous earlier.pdf` notes a drift from the earlier chunk, so that a change is a choice, not an accident.
- A detail that must be read but is not the point is one size below the body (`\notetext`); a figure's label
  and its citation are small (`\figlabel`, `\figcite`); small grey text is only for what need not be read
  (citations, provenance). Captions, source tags and footers may be smaller, but nothing the audience must read.
- Suggested defaults when there is no example deck: on a 16 x 9 cm page, body text of about 11 pt, a median
  body word height of at least 1.75 percent of page width and at most about 150 words per page (formulas
  count extra). These are starting points, not measurements of reference decks.
- One idea per page. If a page needs more, split it or move the detail to the speaker's notes or a backup page.

## Hierarchy and colour

- The same positions on every page, from the top: the navigation when the style has one, the title (the top
  line), the body, the bottom band (the bottom line, then the next question), the footer. The reading deck's
  style adds a subsection tag, a grey subtitle and a source tag, each in its fixed place.
- Titles take one line (about 24 Japanese or 45 Latin characters at the title size).
- **Colours by role**, set once in the project (for example: title navy; headings red; the text under headings
  black; figure labels blue; concept diagrams green): the same role has the same colour on every page, and no meaning is
  carried by colour alone.
- At most three levels of emphasis on a page.

## Layout

- **Set the grid first, then fill it.** One column per figure (usually two or three, equal width), and the
  same slots in the same order in every column: heading, figure, figure label, explanation; the bottom band
  holds the bottom line and the next question. A slot sits at the same height in every column. Do not place
  elements one by one by trial (`\figcol` and `\gutterarrow` in the stage style build this grid).
- **Reserve the figure band first.** Figures are the largest things on the page (the band takes roughly a third
  to a half of the page height); when the page does not fit, cut words, never shrink the figures.
- **Nothing overlaps.** No text on a figure except the figure's own labels and the deliberate marks of an
  annotation; arrows sit in the gutters between columns, at the middle of the figure band; leave visible space
  around every element. An arrow needs no label when the top line already names the method.
  `deck_audit.py --overlaps` reports text lying on an image.
- **Text goes only into its slots**: the heading above the figure ("role: content", an optional short
  parenthesis), the label under it, and an explanation under the label only when the figure cannot be read without
  it (the explanation slot is optional; a page of text lines is cut back). Nothing floats beside or over a figure.
- **Headings stand out; the text under them is quiet.** A heading (a method's name, a figure's heading) is
  larger, bold and coloured. The text under it (what the method does, a weakness) is one size smaller than the
  heading, regular weight, in black; it is read by the audience but does not compete with the heading. Colour
  is kept for headings (a method's heading may carry its key tool in parentheses, one short word) and the few
  marks that carry the page's line (a red "?" or arrow), not for running
  text. `\explain` sets this quiet text (the style's role colour for it is black).
- **Show the figure's own colour legend.** When colour carries meaning, cut the legend (the colour bar) out of
  the same paper figure, put it under the figure, then the key in words
  ([its wording](../../paper-talk-planning/references/page-words.md)).
- **A concept diagram sits under the real figure it explains**: in that figure's column, or in a band under the
  columns when it relates to several; never squeezed beside a figure.
- **A figure that carries the page is large.** The new parts are boxed on the figure itself; pointers to other
  places (→ Fig.n, → the appendix) are small accessories beside the boxes.
- Panels side by side have equal height; margins are equal. Leave open space; a full page is a handout.
- Tables up to about five rows and three columns; otherwise use a list. Avoid mixed-script table cells with
  paragraph columns (baselines drift); use list items.
- Formulas: at most two displayed formulas per page; break a long formula; check the right edge for clipping.
- Boxes take the height of their content. The stage style's `\flowbox` is at least `\flowh` high, grows with its
  text, and shares the tallest height across the page; do not set a fixed box height and do not shrink text to
  make it fit. Before release, `deck_audit.py` must report no words drawn over each other and none outside the
  page (it exits 1 otherwise): an overflowing box, a label printed on text and a closing line running into the
  footer all show up there, without a LaTeX warning.

## Figures and code

- Text inside a figure made for the talk is generated at the final size, so that its labels are legible.
- **What may be done to a figure.** Its content is never changed; fitting it to the page is allowed. Allowed:
  choosing the panel or range (cutting a box), trimming blank margins, enlarging or reducing with the aspect ratio
  kept, and laying annotations over it or beside it (numbered marks, framed terms, arrows), the original file
  staying untouched. Not allowed: retouching, recolouring, removing or rewriting labels or numbers, changing the
  aspect ratio. `scripts/crop_source.py` makes the cut as a new image and records source, page, box and hashes in
  a manifest. The credit says the figure is cut out (and enlarged) and, for a picture under a licence that asks for
  it, a short "changed: trimmed" (cutting is an adaptation; a share-alike licence then applies to the adaptation).
  Do not carry the page's margins or the source's own caption along.
- **Where a picture comes from, in this order:** the source's own figure; a figure of a paper it cites; an existing
  picture under an open licence (CC BY, CC0, public domain) from a trustworthy place (an open-access paper,
  Wikimedia Commons); then **ask the user**, with a substitute proposed, even when it is free. An AI-made picture
  is avoided: only with the user's permission for that picture, labelled on the page as AI-created, never for data
  or results. Record every picture taken from outside the source (work, author, licence, address, date, changes)
  and the searches that found nothing; the intake record of
  [literature intake](../../reading-reference/references/literature-intake.md) takes `kind: figure` for this. A
  licence that asks for credit gets a short credit on the page.
- **Every figure carries a label**, as the paper writes it ("Figure 2", "Figure 2B"); name the panel when it helps
  the audience find what is shown. A figure may be used by a panel; the figure is not skipped.
- **Sources and links on the page are short and sit right after the figure label** ("Figure 2B (Example et al.
  2020)", the link on the author-year words, in the small `cite` size): no separate long source line. The full
  record (address, licence, hash) is kept in the project's sources file, the appendix or the notes. Credits that a
  licence requires stay, in a short form, near the same label.
- **Line breaks where they read well.** Break a heading or a short phrase by hand where it reads well; `\ph{...}`
  keeps a phrase together when that helps. `deck_audit.py deck.pdf --wraps` notes lines that wrap inside a phrase
  (a note, not a failure).
- A picture made for the talk (other than a concept diagram of words and arrows, which needs no tag) or a
  supplementary experiment carries a visible chip saying so (who or what produced it; AI-written code is never
  called the speaker's own). Labels such as "Figure 1-A" are for figures inserted from a paper.
- Code: follow [code pages](code-pages.md). One function or step per page, left column about 60 percent of the
  width at 7 pt or more, a numbered "look at" list on the right, no line counts in titles, provenance of the code
  stated. `deck_audit.py` may flag a code page as small text; that is expected for the code only.
- A root's shared example is the same cut-out at the same place on every subsection of that root, so the audience
  recognizes it; a method's specific example appears only on that method's pages
  ([roots and lenses](../../reading-reference/references/roots-and-lenses.md)).

## Bilingual decks

Both languages share the layout and page count. Shorten each language separately to fit; check both renders.
