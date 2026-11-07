---
name: reading-proof-review
description: Turn a mathematical result's proof, either your own manuscript or someone else's paper, into one private HTML page that separates the key steps from the standard ones, shows the review findings and the difference from prior work, and gives a hedged paper-viability indicator. Builds a sourced step ledger, a dependency diagram, folded proofs, a key-versus-standard comparison and rule-capped verdict. Also builds a proof-centred reading book: blocks, reason-before-formula derivations, cross-linked HTML and one PDF. Not the adversarial review itself, not slides, not a public page.
---

# Proof-review reading page

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use when the user wants to see, on one page, where a result's proof is decisive and where it is
routine, whether it has holes, how it differs from prior work, and whether it looks like a paper.
The result can be the user's own manuscript or a published paper. The page is for understanding
and deciding; it is a local single file, not a web publication and not a certificate.

Resolve `<scripts>` to this skill's real `scripts/` directory (follow symlinks first); pass paths
as arguments instead of relying on the shell's current directory.

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
5. **Page.** Write the step bodies and the review data, build with
   `python3 <scripts>/build_review_page.py <spec-dir> --out <page.html> --lang <user's language>`
   and verify with `check_review_page.py`, then look at the rendered page
   ([page contract](references/page.md)). Math needs KaTeX: `fetch_katex.py` downloads a pinned,
   integrity-checked copy into a cache once the user agrees.

## Proof-centred mode: follow the proof itself

When the user wants to *follow the proof* rather than judge it (every transformation traceable, blocks instead of many
steps, difficulty and reason shown, a PDF with the full derivation), build the page and PDF from block sources with
`python3 <scripts>/proof_book.py build <project>` and verify with `check`; the format, grouping, context layers,
gap-avoidance rules and the independent-reader check are in [proof book](references/proof-book.md), and a fictional
two-block project is in `assets/proof-book-example`. Prototype one block first, let the user react to the wording,
the amount of narration and the layout, then extend to the other blocks. The PDF is for reading the derivation, not a
paper; the HTML shows the main line and links to the PDF for lines too fine to print.

## Rules that keep the page honest

- Every claim carries a locator in the source. Mark each statement as confirmed, suspected or
  unchecked; never write "correct". The strongest allowed statement is "no gap found within the
  stated scope".
- State who checked what: reviewers that are language models are not an expert's check or a formal
  proof, and the page says so near the verdict.
- Novelty is judged only against the sources actually read. For someone else's paper, the novelty
  claim is the paper's own claim, and a gap found in it is reported, not repaired.
- The class of a step is provisional until the prior-work stage; the page may change it.
- Leave the source manuscript untouched. Corrections found by the review are listed for the
  author to accept; edit only after agreement.
- Keep private research content out of anything that is later published: the page, ledger and
  findings of a real project stay in the project's private workspace. Only generic rules and
  fictional fixtures belong in this skill.
