---
name: reading-proof-review
description: Read an existing paper or proof (your own manuscript or someone else's) and turn what the reading establishes into an explanation page for yourself — a proof review (key versus standard steps, findings, difference from prior work, a hedged viability indicator), a proof book to follow a proof line by line, a companion to present a method-and-code paper by seeing and moving it, or a prose explanation — as a private Reader page on your site or as one standalone HTML. Builds a sourced step ledger, dependency diagram, folded proofs and rule-capped verdict. Not the adversarial review itself, not slides, not a public page.
---

# Read, prove, review, and explain on a page

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use when the user has read, or wants to read, an existing paper or proof and wants a page that makes
the reading usable: where a result's proof is decisive and where it is routine, whether it has holes,
how it differs from prior work, how to follow it line by line, how a method's figures come from its
code, or simply an explanation to read. The page is for understanding and deciding; it is private
(a Reader page or a local file), not a web publication and not a certificate. Long courses from books
are [reading-book](../reading-book/SKILL.md); reading and explaining a source in general is
[reading-reference](../reading-reference/SKILL.md).

Resolve `<scripts>` to this skill's `scripts/` directory (`.agents/skills/reading-proof-review/scripts`
from the workspace root); pass paths as arguments instead of relying on the shell's current directory.

## Choose what to make, and read only what applies

| The user wants | Kind | Read |
|---|---|---|
| to see where a proof is decisive, whether it has holes, how it differs from prior work, whether it looks like a paper | **proof review** | the stages below; [ledger](references/ledger.md), [prior work](references/prior-art.md), [indicator](references/indicator.md), [page](references/page.md) |
| to follow a proof line by line, every transformation traceable | **proof book** | [proof book](references/proof-book.md) |
| to present a method-and-code paper by seeing and moving its figures | **companion** | [companion](references/companion/overview.md) and the files it links |
| to understand a concept, result or paper by reading | **prose page** | [prose](references/prose.md) |

For every kind: the [honesty rules](references/honesty.md), and [where the page goes](references/routes.md)
(the private site's Reader page when the workspace has a site, otherwise one standalone HTML whose master
stays in `reading/<slug>/` with a copy in `output/`). Do not mix the two routes for one page.

## Stages

Each stage ends with something the user can react to. Run them in order, and stop for the
user's reaction after each unless the user has asked to run through to the page.

1. **Ledger.** Read the source of truth and write `steps.json` following the
   [ledger contract](references/ledger.md): steps with dependencies, origin and class
   (key / semi-key / standard). Run `python3 <scripts>/check_ledger.py steps.json`. Present the key
   steps with the reason for each class.
2. **Review.** Hand the frozen statement to [proof-adversarial-review](../proof-adversarial-review/SKILL.md),
   which owns the panel, its independence rules and the report format. Merge its findings into the
   page data; this skill never edits the manuscript.
3. **Prior work.** Compare against the sources the user named, following
   [prior-work comparison](references/prior-art.md). A source that could not be read is stated as
   unread, never filled in from memory.
4. **Indicator.** Fill the axes and facts under [the indicator rules](references/indicator.md) and
   check them with `python3 <scripts>/indicator.py review.json`.
5. **Page.** Write the step bodies and the review data, then build the page by the
   [route that applies](references/routes.md): on the site, `export_site_page.py` writes the same spec as
   a Reader page; standalone, `build_review_page.py <spec-dir> --out <page.html> --lang <user's language>`
   and `check_review_page.py`, then look at the rendered page ([page contract](references/page.md)). Math
   needs KaTeX: `fetch_katex.py` downloads a pinned, integrity-checked copy into a cache once the user agrees.

## Proof-centred mode: follow the proof itself

When the user wants to *follow the proof* rather than judge it (every transformation traceable, blocks instead of many
steps, difficulty and reason shown, a PDF with the full derivation), build the page and PDF from block sources with
`python3 <scripts>/proof_book.py build <project>` and verify with `check`; the format, grouping, context layers,
gap-avoidance rules and the independent-reader check are in [proof book](references/proof-book.md), and a fictional
two-block project is in `assets/proof-book-example`. Prototype one block first, let the user react to the wording,
the amount of narration and the layout, then extend to the other blocks. The PDF is for reading the derivation, not a
paper; the HTML shows the main line and links to the PDF for lines too fine to print.

In this mode the review is part of the page, not a separate report: run the independent panel
([proof-adversarial-review](../proof-adversarial-review/SKILL.md), including a numerical check), **repair the blocks**
for every finding that can be repaired (re-check repaired lines with a fresh checker, at most three rounds), turn what
cannot be repaired into a supplement or an open finding, and record validity, risks, findings and limits in
`review.json` (see the review layer in the proof book reference). The page then shows a front section with the
range checked, the risk map and the findings with their fate, a box per block, and a review line in every step.

## Rules that keep the page honest

They are in [honesty](references/honesty.md) and apply to every kind. The ones a proof review leans on
most: every claim has a locator and a status (confirmed, suspected, unchecked); the strongest statement
is "no gap found within the stated scope"; model reviewers are not an expert's check; novelty is judged
only against sources actually read; the class of a step is provisional until the prior-work stage; the
source manuscript is never edited by this skill.
