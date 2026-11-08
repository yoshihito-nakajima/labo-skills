---
name: paper-talk-planning
description: Plan a talk that introduces a paper or survey, page by page, from the source PDF and example decks. Fixes section and subsection weights, source locators, figure explanations, code placement and the links between sections, subsections and slides before any slide is built. Not slide production, not manuscript structure.
---

# Plan a paper-introduction talk

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

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

Read the [full workflow](references/workflow.md) before planning. The steps:

1. Fix the inputs: the companion page when one exists, the source PDF and version, example decks, audience, language and time (asked each time).
2. Map the source by page with `scripts/source_map.py`; look at every figure; read an existing reading note and its card data before planning.
3. Calibrate page capacity by measuring the example decks.
4. Weigh sections and subsections by the talk's purpose, with a role for each page.
5. Reconstruct the motivation of every concept, following the paper's order unless the user chooses another story.
6. Design the links: a section map and the transition table at every level.
7. Take figures, code and computations from sources first; anything made for the talk is the last resort and labelled.
8. Write the script first, then transcribe it into the page; write the per-slide plan with locators.
9. Check and decide: figure order, reading primer, `scripts/plan_symbols.py`, locators; list unverified items and ask only about decisions that change the plan.
10. Hand over the plan and stop. After the user confirms it and the pages are built, review in two stages: the motivation review, then the blind referee.

The plan does not certify the source's mathematics. When the plan relies on a
claim whose statement looks inconsistent, say so in the plan and in the slide
that shows it.
