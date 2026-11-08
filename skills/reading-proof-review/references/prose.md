# A prose explanation page

For a reader who wants to understand a concept, a result or a paper by reading: the question, the
idea, the decisive step, the limits. It is the plain case of this skill; a proof review, a proof
book and a companion add structure for judging, following or moving.

## Before writing

Fix the source and its version, the reader and what they should be able to say afterwards, and the
visibility (private reading page, a public-edition draft, a release: [website-publishing](../../website-publishing/SKILL.md)
owns the last two). Read the actual source and the dependencies the argument needs; a title or an
abstract does not establish an unseen proof. For a substantial paper or proof, reconstruct it with
[reading-reference](../../reading-reference/SKILL.md) first.

## Writing

Follow the [reader-pull rules](../../mathematical-exposition/references/reader-pull.md): the conclusion,
a picture, why it matters and the key idea on the first screen; each section opens plainly and closes by
raising the next question; terms are defined where used; every step has its reason; figures do work.
Headings are natural claims or questions, without role labels. The page reads fully without following a
link, and repository paths or file names never appear on it. The [honesty rules](honesty.md) apply.

## Format

Authored Markdown in the site generator's dialect: `+++` frontmatter (title, slug, language), headings,
lists, pipe tables, quotes, fenced code, `$inline$` and `$$display$$` mathematics, links and
`[text](#anchor)`, nested folds `::: details Summary {#anchor}` ... `:::`, and a figure on its own line,
`![alt](asset:name.svg)`, read from `figures/<slug>/name.svg` beside the page. Raw HTML is shown as text.
A fictional example is `assets/prose-example/example-prose.md`.

On the standalone route, build it with `scripts/build_prose_page.py`; on the site route, place it under
`website/content/private/` ([routes](routes.md)).

## Before it is called ready

A page only its author has read is a draft. Run the
[exposition-review](../../exposition-review/SKILL.md) loop on the rendered page (flow review, critique,
triage, fresh re-review), and for a page revised from an earlier version run
`website-publishing/scripts/check_citations.py` against the previous version so no citation dangles and no
reference entry is dropped. Check the mathematics, figures and links on the actual result.
