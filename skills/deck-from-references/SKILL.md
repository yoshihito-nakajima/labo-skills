---
name: deck-from-references
description: Build or revise Beamer slides for a paper-reading or research talk so that they look and move like example decks the user supplies. Covers the style card taken from the examples, links between sections, subsections and slides, a reusable dark navigation-first Beamer style, design rules (text size, density, alignment) and measured checks of the PDF. Not the talk plan, not the audience and accuracy criteria.
---

# Build slides in the manner of example decks

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use this skill to produce slides that resemble example decks. The plan comes from
[paper-talk-planning](../paper-talk-planning/SKILL.md); audience, accuracy, figures
and pacing criteria come from [slide-authoring](../slide-authoring/SKILL.md). To
shape this skill and a concrete deck together through previews, follow
[skill-tuning](../skill-tuning/SKILL.md). Build with `labo-build`. Keep the user's
colour, language and length choices in the project and the author profile, not here.

## Workflow

1. **Read the examples as renders, not as text.** Put pages side by side with
   `scripts/contact_sheet.py` and measure each deck with `scripts/deck_audit.py`
   (words per page, text size relative to the page). Fill the style card of
   [style card](references/style-card.md). When the user names several examples
   and wants "the good parts", record for each element which example it comes from.
2. **Build in stages** ([staged build](references/staged-build.md)): the skeleton (every page
   with one sentence) first, then chunks of the size the user names (usually 1 to 4 pages), each shown and
   answered before the next; reactions go to `REACTIONS.md`. Never build the whole deck at once unless the
   user says so. The first chunk is **three to five representative pages** (title, outline, a content
   page with a figure or formula, a section opener, a code page when the talk has
   code). Compare them with the examples on one sheet and fix the differences
   before building more. Show the preview and use the user's reaction as the
   evaluation.
3. **Build every page with the shared pieces.** `assets/beamer/talkstyle.sty`
   gives the navigation header with progress bar, subsection tag, title and grey
   subtitle, closing bar, panels, source tag, figure caption and code style, and a
   language switch (`\T{English}{日本語}`). Use one source with two thin roots per
   language so that pages correspond one to one and the build slugs differ. See
   `assets/beamer/example.tex`.
4. **Link everything, and write the why.** Apply [transitions](references/transitions.md):
   each section, subsection and page states what was settled, what is open and what the
   next unit answers, and every major concept follows the motivation chain
   ([order in plan format](../paper-talk-planning/references/plan-format.md)). Take
   figures by cutting them out of the source (`scripts/crop_source.py`), never by editing them. Take
   figures, code and numbers from the source and its cited originals before making
   any; credit them as person, publication and title.
5. **Roles.** On every page that presents a method or algorithm mark what it inherits,
   what is kept, what fixes the obstacle, what has another aim, what is bookkeeping and what limit leads on ([roles](references/inherit-new-forward.md)).
   **Code pages** follow [code pages](references/code-pages.md): numbered markers in
   the code, a "look at" list saying what to see and what is characteristic, a
   provenance tag that never calls AI-written code the speaker's own, no line counts
   in titles. `scripts/extract_code.py` extracts the functions and places the markers.
   **Words** come from the page's script ([the script and the words on the page](../paper-talk-planning/references/page-words.md)).
   **Figure pages** use [figure reading](references/figure-reading.md) as far as the page needs it: the full ladder (see,
   learn, trouble, hand-off, with numbered marks) for a figure that shows a problem.
6. **Make the design pass** with [design rules](references/design-rules.md):
   length against the example deck, sizes by role (a page may adjust them), the grid with nothing overlapping,
   one-line titles, figure labels, formulas that fit, code length.
7. **Review.** Run the two-stage review over every page of both decks, in both stages with fresh
   agents ([motivation review](../paper-talk-planning/references/motivation-review.md), then
   [blind referee](../paper-talk-planning/references/blind-referee.md)).
8. **Check the result.** Build both languages without overfull vertical boxes; run
   `scripts/deck_audit.py` and compare with the examples; look at every page at
   presentation scale, not zoomed; place a sample next to the examples again. Report
   what was inspected, which pages were measured and not looked at, and whether
   timing was rehearsed (an estimate is not a rehearsal).

## Companion first; reading deck and stage deck otherwise

When a companion page of the paper exists, build one source with two builds (the main deck, and the
deck with appendix) tagged with the companion's units and checked by `scripts/link_companion.py`; see
[decks from one plan](references/two-decks.md). Without a companion:

A talk often needs both: a dense, source-anchored deck for understanding and a
visual, arrow-based deck for presenting. They differ in unit, density and how links
are shown; derive the stage deck from the reading deck with no new claims. See
[two decks](references/two-decks.md); the stage style is
`assets/beamer/flowstyle.sty`.

Do not copy an example's content or wording. Do not shrink text to make a heavy page
fit: remove or move material, or split the page.
