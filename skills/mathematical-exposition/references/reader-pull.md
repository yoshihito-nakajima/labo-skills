# Write an explanation readers can pull through

Use for any substantive explanation meant to be read: web expositions, HTML
pages, reading notes, lecture-style write-ups and longer chat answers. Scale it
down for a short chat reply (conclusion first, terms defined, no stray links),
but do not drop it. The goal is an explanation that a reader who does not know
the definitions, cannot fill gaps between lines, and may stop at any moment
still understands and wants to keep reading.

The explanation should be **longer and gentler than the paper, never vaguer**.
It stretches the paper: it adds the pictures, examples, reasons and connections
the paper left to the reader, while keeping the paper's precision.

## The reader to write for

Write for three readers at once and check each:

- **The hurried reader** reads the opening and the headings, then perhaps the
  first paragraph of each section. They must leave knowing the result, why it
  is interesting and the one idea that makes it work.
- **The reader without the definitions** knows the stated floor (for a
  research exposition: undergraduate calculus, linear algebra, basic proof) and
  nothing of the field. Every other term must be explained where it is used.
- **The reader who cannot read between the lines** follows each step only if
  its reason is written. "Clearly", "it is easy to see", "similarly", "by a
  standard argument" are gaps, not explanations.

A careful expert should still find nothing wrong. Gentleness never licenses a
false simplification; say "roughly" and then give the exact version.

## Front-load the payoff

The first screen of the artifact answers, in this order and in plain words:

1. **The conclusion in one or two sentences.** What is now known that was not
   known before, stated without undefined terms. If a precise statement needs
   jargon, give the plain version first and promise the precise one.
2. **The picture.** A concrete image, small example or figure that makes the
   conclusion feel true or surprising. Prefer one well-chosen figure here.
3. **Why it is interesting.** What was puzzling, broken, or out of reach, and
   what the result now allows. Tension before resolution.
4. **The one key idea.** The move that makes the proof or method work, in a
   sentence a newcomer could repeat.
5. **The route.** A short map: which sections answer which question, so a
   reader can jump to what they want. Write it as questions or claims, not as
   a list of section names.

These five are jobs the opening must do, not labels to print. Do not write
「結論：」, 「ポイント」, 「要するに」 or "Key idea:" in front of them; write the
claim itself as the first sentence, let the picture follow because the claim
asks for it, and let the significance come out of the puzzle it resolves. See
[sound like a person](#sound-like-a-person-not-a-template).

Do not open with scope disclaimers, notation conventions, credits for which
paragraphs are supplements, or a list of prerequisites. Put those briefly after
the payoff, or at the point where they matter.

## Make every section repeat this pattern in small

Each section is a short story with the same shape as the whole:

- **Opening (1--3 sentences):** take up the question or result the previous
  section left, and state what this section will establish, plainly and in
  words drawn from the content rather than a fixed frame. A
  reader who reads only this opening learns the section's conclusion.
- **Body:** the definitions, picture, argument and example that earn that
  conclusion, in the order the reader needs them.
- **Closing (1--2 sentences):** say what is now in hand and raise the
  question that the next section answers. The closing is the hook; the next
  opening must catch it.

Headings should tell the story on their own. Reading only the headings in
order, a reader should get the argument's spine. Use claim-shaped or
question-shaped headings in the reader's words ("Four points break the old
inequality", 「四点の空間で旧不等式が崩れる」, 「観測直径とは何か」). Do not prefix
headings with role labels (「問い｜」, 「定義｜」, 「背景｜」, 「結論｜」, "Background:");
the role is the section's job, shown by its opening, not printed in its title.
Only source-aligned reading notes keep visible `role | point` headings, under
[roles and headings](roles-and-headings.md#where-role-labels-are-visible).

## Define like a paper, explain like a teacher

Definitions must be as exact as the paper's, and built only from words the
reader already has. For each new concept that carries an argument:

1. **Why we need it now** — one sentence tied to the current question.
2. **Plain-words version** — what it measures or captures, in everyday terms.
3. **Exact definition** — with types/domains of every symbol, quantifiers and
   hypotheses, using only previously defined terms or the reader floor.
4. **A small example and, when useful, a non-example** — computed, not just named.
5. **What it is for** — how this concept will be used in the next steps, and
   how it relates to concepts already introduced (special case, generalisation,
   tool, obstacle, dual, measurement of ...).

Run an **undefined-term scan** before delivery: list every technical term and
symbol in order of first appearance; each must be defined before or at that
point, belong to the stated reader floor, or be explicitly marked as a black box
with what the reader needs to know about it. Prefer fewer new terms: if a term
is used only once, describe the thing instead of naming it. Keep a **term budget**
per section; introducing more than a few new concepts in one section usually
means the section should be split or a concept postponed.

Repeat a definition, in short form, when it is used again after a gap. The
reader should not scroll back.

## Close the gaps between lines

For each step of an argument, the text says what it uses and why it follows.
Every equality, inequality, choice of constant and "without loss of generality"
gets a reason the reader can check. If a routine computation is compressed,
state what is being computed and what the result is, so the reader could redo
it. If a step is genuinely omitted (black box, long computation), say exactly
what is omitted and where the reader would find it — and still give the idea.

Before a long argument, give its plan in two or three sentences ("we compare A
with B through C; the only delicate point is D"). After it, say what was proved
in words. The reader should never be inside a proof without knowing where it
is going.

## Say the core thing several times, from new angles

The central idea deserves several passes, but each pass must add a new angle so
it never feels like repetition. Useful angles:

- words → formula → figure → computed example;
- the general statement → the smallest case where it is non-trivial;
- what happens at the extremes or in the limit;
- why the naive approach fails (the counterexample) → what the fix changes;
- the same idea seen from the proof, then from an application;
- a physical, geometric or probabilistic intuition, clearly labelled as one.

Never restate a paragraph in near-identical words. If a recap is needed, make
it shorter and sharper than the original, or tie it to the new use.

## Draw the reader's line of interest

At each paragraph end, predict the question a curious reader now has ("but why
can't we just ...?", "does this always work?", "what does this look like for a
circle?"). The next paragraph should answer that question, or explicitly park
it ("we return to this in §4"). Useful moves:

- **question before answer** — pose the puzzle, then resolve it;
- **surprise early** — put the counterexample, the unexpected value or the
  failed naive attempt before the fix;
- **small to general** — compute a concrete case, then reveal that the
  pattern is the theorem;
- **stakes** — say what would break, or what becomes possible, if the claim
  were false or true.

Do not manufacture drama or exaggerate significance; the interest must come from
the actual mathematics.

## Keep one thread through the whole page

Local continuity between adjacent paragraphs is not enough; the page as a
whole needs a line. Before drafting, write the thread in a few sentences: the
question, the steps that answer it, and where each step's need comes from.
Then:

- **Tell near topics together.** Two passages about the same object, the same
  idea from two angles, or a problem and its resolution belong in one place or
  in adjacent sections. If they must be apart (source order, a needed detour),
  the later one names the earlier one and says what it adds.
- **Every detour returns.** A digression (background, side remark, a related
  result) states why it is taken and ends by bringing its result back to the
  thread.
- **Every promise is paid.** A question raised is answered, or explicitly left
  open with a reason; an answer is never given before its question.
- **Order by need.** A definition, picture or lemma comes when the reader
  first needs it, not in a front block and not after it was used.

After drafting, the [exposition-review](../../exposition-review/SKILL.md) loop
checks this thread with a reader who has not seen your plan.

## Connect concepts explicitly

Whenever a concept, lemma or quantity appears, say how it connects to those
already on the page: what it is built from, what it controls, what it replaces,
and which later step needs it. When more than three concepts interact, give a
small concept map (diagram or table) once, and point back to it with its own
words, not with a link. The reader should be able to say, for each object, "this
is here because ...".

## Place figures where they do work

Add a figure where the reader would otherwise have to imagine a shape, a
comparison, a process, a counterexample or the relationship among several
objects. For each figure:

- before it, tell the reader what to look at;
- the caption alone states what the figure shows and what it supports;
- after it, say what was learned and use it in the next step;
- label schematic illustrations as such; never fake data.

A figure placed only for decoration, or a figure the text never uses, is
removed. A paragraph that describes a picture in words for more than a few
lines is usually a missing figure.

## Keep the page self-contained

The explanation must be readable without following any link. Links, file
paths and cross-references support the reader; they never carry the
explanation.

- State the needed content in place instead of "see X" or "as in the other
  note". A pointer may follow the content, never replace it.
- In reader-facing prose, do not expose repository paths, `.md` file names,
  internal note titles, work logs, tool names or process remarks. Cite sources
  by a compact locator (paper, version, theorem/section) at the point of use,
  together with the cited content, and collect them in the annotated
  reference list at the end.
- Avoid link clusters in running text. One link per claim at most, placed where
  the reader would actually want to check.
- **References carry their content.** A citation is not a place to send the
  reader; the page says what the cited work gives. Self-containment is reached
  by writing the cited content in, never by removing citations.
  - **At the point of use**, state the cited result the argument needs in
    usable form: the statement with its hypotheses and the objects it applies
    to, in the page's notation, plus one or two sentences on why it holds or
    what idea it rests on when that helps; then check that its hypotheses hold
    here. "By [8, Theorem 6.22]" alone is a gap. A definition taken from a
    cited work is written out like any other definition.
  - **In the reference list** at the end, each entry gives the bibliographic
    data (authors, title, venue or arXiv identifier with version, year) and an
    annotation of a few lines: what the work is about, exactly what this page
    takes from it (result, definition or construction, with its locator) and
    how that enters the argument; for prior work used for comparison, what it
    proved and how the present result differs. A reader who reads only the
    list should know what each work contributes.
  - Every citation in the text — numbered like `[8, Theorem 6.22]` or by name —
    resolves to an entry on the same page. If the page keeps the source paper's
    numbering, keep that numbering. Mark what the cited work states and what
    this page adds, as for any source.
  - When rewriting or shortening a page, compare citations, entries and
    annotations with the previous version; a dropped entry, a dangling `[n]`
    or a citation reduced to a bare number is a regression, not a simplification.
- In chat, the same rule holds: answer in prose first; file references, if
  any, go in one short line at the end, and only when the user needs to open them.

## Sound like a person, not a template

The structure above is about what each passage does for the reader. When it
shows through as visible scaffolding, the text reads as machine-written and the
reader stops trusting it. Make the content carry the structure.

**Signs of template prose, to remove:**

- Role labels in headings or paragraph starts (「問い｜」, 「定義｜」, 「背景：」).
- Labels and signposts that announce instead of saying: 「結論から言うと」,
  「ポイントは」, 「重要なのは」, 「ここが肝」, 「まとめると」, 「一言で言えば」,
  「本質的には」, 「直感的には」 used as a reflex, "In summary", "The key insight
  is", "It is worth noting".
- Meta-narration of the text itself: 「この章では〜を見ていく」, 「以下で詳しく
  説明する」, 「では、さっそく〜」, 「〜について考えてみよう」 at every opening.
  A section may say where it goes, but by stating the question, not by
  describing the act of explaining.
- Every section opening and closing built from the same sentence frame. The
  function (take up, state, hand on) stays; the wording must vary with the
  content.
- Reflexive triads, bullet lists for what is really an argument, bold on every
  other phrase, and a recap paragraph after every section.
- Defensive contrasts and denials as rhetoric: 「AではなくBだ」, 「単なる〜では
  ない」, "not just X but Y". State B directly; keep a negation only when its
  logical content matters.
- Inflated emotion and evaluation: 「驚くべきことに」, 「美しい」, 「非常に強力」,
  「画期的」, exclamation marks. Let the example show the surprise.
- Hedging stacks and filler: 「〜と言えるだろう」, 「〜と考えられる」 where a
  plain claim is correct; 「〜することができる」, 「〜を行う」, 「〜という形で」,
  「〜というものは」.

**What natural expository prose does instead:**

- Opens with the thing itself. 「空間の列が近づけば、観測直径も近づく。」 is
  already the conclusion; it needs no label.
- Turns on content, not on connectives. The next paragraph begins from the
  object just reached (「では四点の空間ではどうなるか。」), not from 「次に」.
- Lets an example or a failure create the question, then answers it. Interest
  comes from the mathematics, not from adjectives.
- Uses paragraphs for reasoning and lists only for genuinely parallel items
  (cases, hypotheses, a route map).
- Varies sentence length and ending. In Japanese, avoid long runs of the same
  文末 (「〜だ。〜だ。〜だ。」 or 「〜である。」 repeated), and do not fix on
  体言止め as a substitute. Mix a short plain claim with a longer sentence that
  carries a reason.
- Uses each signpost word rarely enough that it still means something. If
  「つまり」 appears, what follows must genuinely restate in simpler terms.
- Has a voice: the writer chose this example and this order for a reason, and
  occasionally says why in a clause. It reads like a skilled mathematician
  explaining to a colleague from another field.

When in doubt, delete the label or signpost and reread: if the sentence still
works, it was scaffolding.

## Sentence-level clarity

- One sentence, one move. Split sentences that carry two inferences.
- Make the subject explicit; every "this", "it", "the above" has an obvious
  referent in the same or previous sentence.
- Prefer verbs to long noun phrases (Japanese: avoid stacked 「〜の〜の〜」).
- Put the conclusion of a paragraph in its first or last sentence, not buried
  in the middle.
- Use the same word for the same thing throughout; change words only when the
  object changes.

## Readability audit

Before delivery, run these tests on the actual text and repair the first
failure of each:

- **P1 Hurried reader:** From the first screen alone, can one state the result,
  why it matters, and the key idea, without undefined terms?
- **P2 Headings:** Read only the headings in order. Do they tell the story,
  using words the reader knows?
- **P3 Section openings:** Read only the first 1--3 sentences of each
  section. Is each section's conclusion clear, and does each opening take up the
  previous closing?
- **P4 Undefined terms:** Every technical term/symbol is defined at or before
  first use, is in the reader floor, or is a labelled black box. Count new
  terms per section.
- **P5 Gaps:** Pick the three hardest steps. Is the reason for each written,
  with its inputs? Any "clearly/similarly/standard" left?
- **P6 Next question:** At each section end, write the reader's likely next
  question. Does the next section answer it?
- **P7 Angles:** Is the central idea shown from at least two genuinely
  different angles (e.g. formula and picture, general and smallest case)? Is any
  paragraph a near-duplicate of another?
- **P8 Connections:** For each main concept, can the reader say why it is here
  and what it connects to?
- **P9 Figures:** Is every figure introduced, captioned, and used? Is there a
  place where words strain to describe a picture?
- **P10 No links needed:** Mentally delete every link and path. Does the
  explanation still work? Are any internal paths or file names visible?
- **P11 Natural prose:** Search the text for the template signs above
  (role-labelled headings, labels such as 結論/ポイント/まとめ, meta-narration, repeated opening frames,
  rhetorical denials, inflated adjectives, filler). Does each remaining one earn
  its place? Read three section openings side by side: do they sound different
  because their content differs?

These tests complement the continuity and heading audits; they do not replace
fidelity checks. Report any test you could not run (e.g. figures not rendered).
