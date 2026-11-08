---
name: reading-companion
description: Build a private, single-file interactive HTML companion that prepares a reader without the field's background to present a method-and-code paper, read before its detailed reading note. The paper's Summary, Introduction and the lineage of earlier methods (what each was for, where it is weak) come first; main-text figures in the paper's order are the spine; each figure unit explains what the figure claims and how to read it, joins its selling point to the code selling point and the code blocks its difference comes from, shows the earlier method's code beside the authors' code with what each block does and where it comes from, and gives one run with controls on small synthetic data for both methods; a supplement opens with the whole-code map and reads the code step by step from the first step. For understanding and presenting; not slides, not a public page.
---

# Interactive companion for presenting a method paper

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use when a detailed reading note of a paper whose contribution is a method with code exists or
is being written (see the [method-paper profile](../reading-reference/references/method-paper-profile.md))
and the user wants to be able to present the paper: to explain each main-text figure, the code
that produces it, and what differs from the earlier method, by seeing and moving it. The page is
read before the note, by a reader who lacks the field's background: words, pictures and small
examples come before symbols, code and controls, and supplements fold. The note stays the source
of truth: the companion adds no claim the note does not carry
([reading-reference](../reading-reference/SKILL.md) owns sources, provenance, reproduction levels,
the request list and unobtained material). Slides belong to
[deck-from-references](../deck-from-references/SKILL.md); web publication to
[website-publishing](../website-publishing/SKILL.md).

## The companion is private

The HTML is one file that opens in a browser on this machine without a network; nobody else
sees it unless the file is handed over or put on a web server. Write it and its data under
`reading/<slug>-companion/` (or another path the workspace's parent Git ignores;
`scripts/check_companion.py --workspace` verifies this). Never upload, publish, attach to a
public page or hand to `website-publishing` unless the user explicitly asks for that as a
separate task: the page embeds cut-outs of the paper's figures and code excerpts. The skill
itself is generic and public; its examples are fictional.

## References

- [Ideal and page layout](references/companion-ideal.md): the purpose (presenting the paper),
  the reader, what they must be able to answer, the correspondence table, the order of the page.
- [Figure unit](references/figure-unit.md): one main-text figure — claim, reading, figure
  selling point ↔ code selling point, where the difference comes from, one run with controls on
  synthetic data, presenter's notes.
- [Comparison](references/comparison.md): the earlier method's code beside the authors' code,
  what each block does, where it comes from and what differs, the same / changed / only-in-one
  colours, both methods' parameters and runs.
- [Step unit](references/feature-unit.md): the supplement that reads the code from step 1.
- [The pair](references/pair.md): the note (PDF) and the companion (HTML) kept as one pair: `PAIR.json`,
  `new_pair.py` / `build_pair.py` (start and build both halves, provisional), `check_pair.py` (stale builds, treated comparisons and figure differences present on both sides,
  intake record), `archive_pair.py` (copy into the local-only corpus).
- [Section-structured page](references/section-page.md): for survey papers read section by section — a common
  collapsed layout, a head panel per section, original region beside the faithful translation, Steps and comparison
  cards per code section; `scripts/check_section_record.py` checks the record and
  `scripts/build_section_page.py` builds the HTML and the TeX parts from it.
- [Fidelity](references/fidelity.md): the authors'-code parameter grid, reproduction levels,
  re-implementation only with a parity record, provenance labels, licences.

## Workflow

1. **Inputs and readiness.** The detailed note (PDF and `.aux`, for labels and pages), its talk
   plan with understanding checks if any, the authors' code at a fixed commit, the code of each
   earlier method shown, data, and the paper's figures. Start from the note's
   [figure readiness review (R32)](../reading-reference/references/review.md): for each main-text
   figure, the claim and reading, the code behind it, the reproduction level and the open
   [request list](../reading-reference/references/resource-ledger.md#request-list). Give the
   request list to the user; a missing input is reported, not invented.
2. **Plan** (`COMPANION_PLAN.md` beside the output, then `companion.json`): the shared
   introduction; the Summary, Introduction and lineage (from the note's overview table); the
   correspondence table (one row per main-text figure: figure selling point,
   code selling point, earlier method, level); for each figure the parts of the
   [figure unit](references/figure-unit.md); for each step the parts of the
   [step unit](references/feature-unit.md); for each comparison the
   [correspondence list](references/comparison.md); the parameters of both methods (defaults,
   grids with values that make the effect obvious, presets with their expected change); the
   sources used; the code map (the entry function's code split into step blocks), which opens the
   supplement; for each figure where its difference comes from, one run with controls on synthetic
   data and a `check` for every *learn*. Take explanations from the note and its glossary, and the
   lineage, code-block notes, difference sources and values from the note's matching parts
   ([method-paper profile](../reading-reference/references/method-paper-profile.md)); a part the
   note lacks is added to the note first. Write the storyline layer of `companion.json` first and
   check it alone with `scripts/check_outline.py`: the shared introduction, the method map, and the
   `difficulties` (the obstacles the paper names, each saying why the obvious route or the earlier
   method fails) with, for every step, `why` it is needed here and the `answers` it gives. Fix the
   story before writing units; the page then shows each obstacle with the steps that answer it.
3. **Runs** (about a minute each, at most five: [compute budget](references/fidelity.md#compute-budget-understanding-not-exact-restoration)). Run the authors' code and the earlier method's code over their grids, on the same
   input, at the highest reproduction level available, in an isolated environment
   ([execution](../reading-reference/references/methods.md#execution-environments)); save one small
   result file per step with the script, commit, data identity, level and seed, and write its
   [run card](references/fidelity.md#say-what-was-run).
4. **Build everything in one pass**: every main-text figure unit and every step unit, with
   `scripts/build_companion.py companion.json --out ...`. While building, partial states may be
   checked with `--allow-pending`; a page with pending units is not handed over, and no single
   unit is shown first as a trial. (Understanding material is built in one pass; only slides are built
   in stages: [staged build of slides](../deck-from-references/references/staged-build.md).)
5. **Check** the whole page with `scripts/check_companion.py` (no pending units; privacy, no
   external resources, size, duplicate ids and in-page links that lead nowhere in the rendered page
   (needs Chrome/Chromium; skipped with a note otherwise); every main-text figure in order with claim, reading, presenter's notes
   and the data it was run with; every run with its run card; every figure link resolving to a step;
   comparison ranges inside the excerpts; terms and labels for every parameter; presets on grid
   points; labels present in the note; code excerpts verbatim; grid coverage for both methods;
   parity records; sources with commits and data identities), then look at every unit in a browser
   and press every preset.
6. **Review with the user's view.** Hand over the whole page with a review proposal (what to check,
   against which criteria, by whom, in which order; by default the
   [exposition-review](../exposition-review/SKILL.md) loop on the page's text, alongside the checks above) and ask the user how the review should go before
   reviewing; then review and repair.

Report what was run and at which level, which units were looked at in a browser, the open
request list, and what the companion does not show.
