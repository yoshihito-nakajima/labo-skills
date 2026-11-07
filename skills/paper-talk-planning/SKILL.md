---
name: paper-talk-planning
description: Plan a talk that introduces a paper or survey, page by page, from the source PDF and example decks. Fixes section and subsection weights, source locators, figure explanations, code placement and the links between sections, subsections and slides before any slide is built. Not slide production, not manuscript structure.
---

# Plan a paper-introduction talk

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use this skill when the user wants the design of a talk that introduces a paper,
survey or method before slides exist: what to say in which order, how heavy each
section is, what each page shows. The product is a written plan the user can
correct. [deck-from-references](../deck-from-references/SKILL.md) builds the
slides from it; [slide-authoring](../slide-authoring/SKILL.md) owns audience,
accuracy and pacing criteria; [reading-reference](../reading-reference/SKILL.md)
owns reading and explaining the source; [paper-structure](../paper-structure/SKILL.md)
is for manuscripts, not talks.

## Workflow

1. **Fix the inputs.** When a companion page of the paper exists, it is the primary input: take the
   claims, figure readings, differences, lineage, code map, presenter's notes and checks from its
   units (`link_companion.py list`) and plan the main body and an appendix from them
   ([decks](../deck-from-references/references/two-decks.md)); the detailed note and the PDF are
   opened only to settle a doubt. Audience, time and language are asked of the user each time. Source PDF and version, example decks the user wants to
   resemble, audience (for example mathematicians who want the method), language(s),
   whether source order must be kept, and time (use only what the user states;
   "no limit" means judge by coherence, not by a slot).
2. **Map the source by page.** Run `scripts/source_map.py <paper.pdf>` for headings,
   captions, equation numbers and image counts per page; the output is a locator
   index, not a reading. Render and look at every figure and table before
   explaining it. Read the equations and algorithms from the rendered page when
   the extracted text is garbled, and list any apparent misprints in the source
   instead of silently correcting them.
   If a detailed reading note of the source already exists, read it in full before
   planning. If the note keeps its background cards as data
   ([card data](../reading-reference/references/roots-and-lenses.md#card-data)), run
   `scripts/cards_to_plan.py <cards.json>`: it checks the data with `check_cards.py` and writes
   the root list and motivation-card skeletons with every source kept. Only for a note without
   card data, run `scripts/notes_map.py <notes.pdf> --cards` (the counterpart of `source_map.py`
   for a note: subsections from its contents, role headings, source-page references and
   provenance markers by page). Then tabulate, per subsection: its background card (what it uses,
   its root, shared example, lens, applied, specific and limit examples), its code reason cards, and the provenance class of each figure, code unit
   and computation ([reading structure](../reading-reference/references/reading-structure.md),
   [code reason card](../reading-reference/references/application-to-code.md)). Check each
   against the original page before it enters the plan; a claim only the note makes
   (an added explanation) is not evidence. Take backgrounds, roots and code reasons from
   the note rather than re-deriving them, and report what the note lacks.
3. **Calibrate capacity from the examples.** Measure the example decks with
   `../deck-from-references/scripts/deck_audit.py` (words per page, text size) and
   look at their pages. State the density you assume. Do not invent a page quota.
4. **Weigh sections and subsections.** For each source section and subsection give
   the number of pages and the role of each page (opener, method overview, full
   code, selling point or mathematical core, figure with explanation, turn). Weight
   follows the talk's purpose: if the audience wants methods, methods get the
   pages and background gets the minimum that keeps them intelligible. Cover every
   section when asked to, but not at equal weight. Major concepts (the ones the talk
   is for, or that later sections build on) get the full motivation chain over several
   pages; minor ones are kept but thin: the problem in the subtitle, a small failure
   example on the page. Avoid both a handout (too dense) and fragmentation (one idea
   split across many pages).
5. **Reconstruct the motivation of every concept.** A talk that introduces a paper follows the paper from the front:
   the default order of the pages is the paper's order (Summary and Introduction, then its Results in order, and so on);
   it is reordered into another story only when the user chooses that, and the reason is written in the plan. Every page
   carries the passage of the paper where its claim is made (section, paragraph, page); an introduction page takes its claims
   from the paper's Introduction. A figure from later in the paper may be shown as **evidence** for such a claim, marked as
   evidence (or example) on the page, only when the cited passage itself states the claim the figure supports; a figure the
   passage does not bear on is not shown. Within that order, position in the source is a label on the page; the motivation of
   each concept is still rebuilt where it appears. For each
   concept the talk introduces, fill a motivation card
   ([plan format](references/plan-format.md)): the problem, why the previous tool falls
   short on a concrete case, the idea with its definition, how it is computed in practice
   (with the role of each part: new, inherited from the previous method, or leading to the
   next subsection), the root problem it belongs to, and the lens of the method with its shared,
   applied, specific and limit examples ([roots and lenses](../reading-reference/references/roots-and-lenses.md)), what it achieves, and what remains. Look for the motivation in the source first,
   then in the original papers it cites, then in standard mathematics; mark the origin of
   each field. A term must not appear before the page that shows why it is needed. **Each subsection
   reopens the problem**: even when the underlying problem is the same as in the previous
   subsection (for example, unroll the same Swiss roll), its first page restates it on the
   running example, says what this method asks and why the previous method falls short in
   that respect, and gives the sourced reason for the idea, so that the algorithm follows as
   the natural answer. A recap is not a repetition to be avoided: the viewpoint differs every
   time. The reason comes from the source or its cited originals, never from invention
   ([plan format](references/plan-format.md)).
6. **Design the links.** Write the section map of each section first ([plan format](references/plan-format.md)): before, the section's problem, the chain of its subsections, after. Fill the transition table of
   [transitions](../deck-from-references/references/transitions.md) for every
   section-to-section, subsection-to-subsection and slide-to-slide step: what was
   settled, what is left open, what the next unit answers. Mark each link as stated
   by the source (with page) or as the speaker's own.
7. **Take figures, code and computations from sources first.** Prefer, in this order:
   figures from the paper and from the original papers it cites; then existing open-licence pictures from a
   trustworthy place, recorded with licence and credit (see [design rules](../deck-from-references/references/design-rules.md#figures-and-code));
   when none is found, ask the user with a substitute proposed; AI-made pictures only with the user's permission per picture; the authors' published
   code and published numerical results; only then material made for the talk. Anything
   made for the talk (a schematic, an AI-written function, an AI-run experiment) is the
   last resort, kept minimal, adjusted only for clarity, and visibly labelled; the plan lists,
   for each such figure, where an original was looked for. The order and
   the license limits for code are those of
   [reading-reference](../reading-reference/references/application-to-code.md#show-the-adopted-source-code-first). Credit
   every source as person, publication and title ([plan format](references/plan-format.md)).
   When code is wanted, give each subsection that has a method one code page
   ([code pages](../deck-from-references/references/code-pages.md)): whose code it is, the
   three or four lines to look at and what is characteristic there. Split rather than
   shrink long code, and never put a line count in a title. Every figure gets a reading plan: what it shows and
   does not show, its key, axes, colours and source page; a figure that shows a problem also gets the marks, the
   trouble and the hand-off of [figure reading](../deck-from-references/references/figure-reading.md), used as far as
   the page needs them.
8. **Write the script first, then transcribe it into the page** ([the script and the words on the page](references/page-words.md)):
   script with *page* and *spoken* marks (the authority once agreed), the sentence-to-element table, the arrangement
   (the user's mock-up when there is one), the page, and a check both ways; a difference is fixed on the page.
   The script walks through the page: every element it shows (each figure, key, concept diagram, arrow) in the order the
   audience's eye follows, about one short sentence each, how the elements tie together, and the reason. An element with no
   sentence in the script is not on the page; a sentence about something not on the page means the page lacks it. A figure's
   sentences start from its companion reading (*see* and *learn*), so the script says what the figure shows for the page's
   claim, not only what it looks like. Check the script against the page's elements and against those readings, then take the page's words from it: the top line, the bottom line and the next
   question (full short sentences), keywords, the keys in plain words, and a short tie phrase where the audience cannot see a
   tie at once. Every word on the page has its sentence in the script; what the speaker can say aloud is not written on the
   page. How the words are set (sizes, grid, colours) belongs to
   [design rules](../deck-from-references/references/design-rules.md).
   **Write the per-slide plan** in the format of
   [plan format](references/plan-format.md), in source order, with locators.
9. **Check and decide.** The main-text figures are each explained in the body, in the paper's order
   (Fig.1 to Fig.N ascending), whatever the story order elsewhere; a figure may be shown by a few of its
   panels, never skipped. The introduction carries a reading primer before the first result figure: what the
   method's output is made of, what one can learn from it, and every mark, size or colour the later figures use
   (the companion's `primer`); no encoding is used on a result page before the primer introduced it, as no symbol
   is used before its introduction. Run `scripts/plan_symbols.py` on the plan (no symbol used before
   its introduction). Verify every locator against the page, the page count
   against the weights, and that each closing question of a page is answered by
   the next. List the unverified items and the decisions that change the plan (theme,
   page count, language handling), recommend a default for each, and ask only
   about those. Save the plan in the project, not in this skill.
10. **Hand over the plan and stop.** The plan (a skeleton with one sentence per page) is confirmed by the user
    before any page is built; pages are then built in chunks ([staged build of slides](../deck-from-references/references/staged-build.md)).
    **Review in two stages over every page**: first the criterion-based
    [motivation review](references/motivation-review.md), repair; then the
    [blind referee](references/blind-referee.md) with fresh agents that know nothing but the
    audience, repair and rerun until no missing bridge is reported. Report what each stage
    covered.

The plan does not certify the source's mathematics. When the plan relies on a
claim whose statement looks inconsistent, say so in the plan and in the slide
that shows it.
