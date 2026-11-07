# The script and the words on the page

The script comes first and the page is a transcription of it: each sentence of the script that carries the
page's line is turned into something the audience sees (a picture from the paper, a concept diagram, a short
heading), and words are written only where the picture cannot be read without them. The rules below say what
that means; how the words are set (sizes, grid, colours) is in
[design rules](../../deck-from-references/references/design-rules.md). Fictional examples throughout: a
method *Alpha* that draws a route map from location points, and an earlier method *Beta*.

## From the script to the page: the procedure

1. **Script (authority).** Write the script and mark each sentence as *page* (it carries the page's line to the
   next page) or *spoken* (said aloud only, for example how things were studied before). Once the user has agreed
   to it, the script does not change to fit the page; when page and script differ, the page is corrected. The
   script changes only when the user decides so.
2. **Sentence-to-element table.** For each *page* sentence write: what it refers to ("what is this,
   concretely?"), the element that shows it (a picture from the paper, a concept diagram, a colour bar), and the
   words on the page (a short heading taken from the sentence, a single term). Show the table before building.
   It replaces the plan's "On the page" field.
3. **Arrangement.** Place the rows in the script's order, in the order the eye follows; an arrow stands for the
   link between two sentences ("measured this way", "so we must estimate"). A mock-up drawn by the user is the
   arrangement, and it overrides the layout rules of the design.
4. **Build** the page from the table.
5. **Check both ways** before showing it: every row of the table is on the page, and nothing is on the page
   that the table does not list. A difference is fixed on the page. A sentence marked *page* always has words
   in its row (never "none"): a step of a figure, for example, gets a frame on the figure and a short
   explanation beside it; what is meant to be explained aloud belongs to the *spoken* mark.

## Choosing what the audience sees

- **A picture answers "what is this?" for its sentence**, and is the simplest one that shows only that: a
  sentence "measuring each item gives the points in between" gets a picture of the point cloud. A rich
  concrete example whose many labels, colours and numbers bury the point is not used, even when it is a good
  example; look in the same paper for a simpler figure.
- **Pictures placed together continue each other**: the same data with the same colouring, differing only in
  what changes (the point cloud, then the same point cloud with the path drawn on it), and the same cut-out as
  the next page uses, so that the next page can say "the picture you have seen".
- **A heading that names a method carries its key tool in parentheses**: "Beta (spanning tree)", "Gamma (diffusion
  map)": one short word, the thing the method is built on. The text under the heading is then shorter ("thins
  the cells, then joins the groups") and the tool word is not repeated in it. The key tool is the one the
  script names and the audience needs later (the term the next pages use).
- **Words are few.** The page carries headings (short phrases from the script), the term of a colour bar
  ("local density"), arrows and the top and bottom lines. A line of explanation that only restates the picture
  or the script is spoken instead; a page that is a list of text lines is cut back. A figure inserted from a
  paper still carries its label ("Figure 1", with a short citation).

## The script

- **Write it before the page's words.** It walks through the page: every element the page shows (each
  figure, its key, a concept diagram, an arrow, the bottom line) in the order the eye follows, about one
  short sentence each, and the reason of the page. An element with no sentence is not on the page; a
  sentence about something the page does not show means that the page lacks it, or that the sentence goes.
- **It says how the elements tie together**: what the arrow between two figures means, how a concept
  diagram meets the figure above it, what an example does for the top line. A tie the audience cannot see
  at once also gets a short phrase on the page ("this order appears as the shape of the map").
- **A figure's sentences start from its reading.** Before writing about a figure, open its companion unit (claim,
  reads with *see* and *learn*, presenter notes) and the note's section on it. The script says what to look at
  (*see*) and what that tells for the page's claim (*learn*); a figure described only by what is seen ("the two
  runs differ") has not been read. For an evidence figure, the script names which point of the paper passage the
  figure shows and where on it ("Beta's two runs differ, and in one of them station C sits in the middle of the
  line to D"). Every read of the companion that bears on the page's claim is in the script, or the plan says why not.
- **No new claim.** The claims come from the page's paper passage and the companion units; reasons are
  sourced ([plan format](plan-format.md)).
- **Short.** The script is what is said in the page's time, not a lecture.

## From the script to the page

- **The words on the page are the script compressed**: keywords, short phrases, arrows and signs
  (→, =, ↑). What the speaker can say aloud is not written. Every word on the page has its sentence in the
  script (the plan's "On the page" field lists it), and the reason the script gives survives on the page,
  usually in the bottom line.
- **Top line, bottom line and next question are full short sentences.** Subject, verb and, where there is
  one, object are written out ("Alpha は、位置の点群から道の地図を描く"; "Alpha draws a route map from
  location points."): not a noun phrase ("既存の代表：Beta"), not a sentence with its subject dropped, not a
  colon-joined fragment. Japanese lines carry no full stop; English lines end with a full stop, questions
  with a question mark. The top line is the page's claim; the bottom line is what the page established (not
  the title again); the next question is answered by the next page's top line, so its subject appears
  there. The top line fits one line (about 24 Japanese or 45 Latin characters), the bottom line and the
  question about 30. Words inside the page stay compressed; headings are labels and may be nouns.
  `../../deck-from-references/scripts/check_sentences.py` reports the lines that break this.
- **The bottom line says why the page matters, concretely**: what one can now read or do, or why the claim
  holds ("地図を描くと、道の順序と分かれ道が読める"), not a vague capability ("地図で移動を探索できる"). What a
  later page explains is left to that page.
- **Words beside a figure say only what can be read from that figure**: shape, colours, marks, labels and
  caption. What it cannot show (which end comes first on a one-colour map, what an end means) is not
  written beside it: it goes to a page whose figure shows it, to the bottom line, or, when the paper's text
  states it, to a concept diagram carrying that passage. Writing that the figure cannot show it ("the
  direction cannot be read from this figure alone") is allowed. The plan records, per figure, what it shows
  and does not show. When a reading cannot be seen only because the page lacks a key (which colour is which
  type), add the key from the paper's own legend of those colours; do not drop the reading.
- **Keys are plain words.** A figure whose colour, size or marks carry meaning gets a key: the figure's own
  colour bar and the term ("speed") may be enough on the page, with the gloss spoken; when written, the technical
  word comes once, glossed at once in everyday words, with what a high value means ("colour: speed (the brighter,
  the faster the cars)"). Not "yellow = fast" alone, and not a definition with symbols. When the colour is a
  measured marker, add one line on what is measured from each item and what the marker marks, taken from the
  companion's figure units, not from memory, and written per slide. The word a key needs is defined on the
  first page that uses it and not repeated. A page with a figure carries `\colorkey{...}`, or
  `\nocolorkey{reason}` when nothing needs a key. Where the key sits is a
  [layout](../../deck-from-references/references/design-rules.md#layout) rule.
- **Marks say what happens there**, not only a name: not "junction" but "splits in two after B".
- **Emphasis follows the figure.** What the page's figure shows is the main item (large, coloured); items the
  figure does not bear on are quiet (small, grey, one line at most). Do not list the main item and the others
  in one size when only one of them has its evidence on the page.
- **Evidence is a contrast.** A weakness of an existing method is shown beside the paper's method on the same
  input ("look, they differ here"); a figure of the existing method alone is not evidence. The script also says
  which weakness the difference shows, from the figure's reading (above). Why they differ is said later.
- **An example shows what can be read from it.** A figure shown only as an example (`\asexample`, the chip
  "例") is there for its meaning: the words around it say what it lets one read. Whether the method got it
  right is shown on the page that explains the figure, as a contrast.
- **An arrangement has a meaning, and the script says it.** The parts of a page (columns, bands, a concept
  diagram) stand in a relation (what goes in → what comes out → a real use; whole → features; before →
  after; cause → effect; example → general), and each arrow or position means something the audience can
  say. These relations are examples to think with; the user decides each page's arrangement, and the plan
  records it.

## Concept diagram

A diagram of words and arrows (boxes or plain words joined by arrows, a "less → more" gradient, "…" for more
of the same kind), drawn as one draws it in a presentation program. A short note beside a box may say what the
page wants to understand there ("this is what we want to understand").

- **What it draws**: the story of the field that the figure beside it is about, as the paper's text states it,
  with the passage recorded in the plan (for example, the known order of the stations A → B → C or D on the
  line the map is drawn for). Nothing the paper does not say. It is not a picture of the objects.
- **Names and gradients** follow the paper's figure beside it: the same names, and a gradient in the sense of
  the figure's key ("less → more"). Its colour is the page's concept colour.
- **The tie**: the script says how the diagram meets the figure, in the service of the page's top line ("this
  order appears as the shape of the map, so the map lets us read it"); a short phrase on the page says it
  when the audience cannot see it at once.
- **No label.** A concept diagram of words and arrows carries no "concept diagram" tag on the page; its source
  passage is in the plan. Labels ("Figure 1-A", with a short citation) are for figures inserted from a paper.
  Where it sits is a [layout](../../deck-from-references/references/design-rules.md#layout) rule.
