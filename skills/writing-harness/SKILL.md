---
name: writing-harness
description: Run an author-led paper harness in which the author writes the prose and the agent keeps the facts — definition and theorem cards with gap-free reference proofs, a status ladder, staleness of prose after a fact changes, reading-order checks, a story ledger with an undefined-term check, a style ledger applied paper-wide, one build that keeps TeX, PDF, card viewer and reading page in step with the cards (with an editing hook, a watcher and OUTDATED warnings), a local page where the author edits cards with live preview, card templates, and review rounds on frozen parts. Use when the user writes a paper themselves and wants an editor and consistency keeper beside them; for drafting a manuscript from research evidence use paper-writing.
---

# Writing harness

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

The author writes the paper in their own language and voice. The agent keeps
what can be kept mechanically — identifiers, statements, reference proofs,
dependencies, names, style decisions — and proposes, explains and checks.
[paper-writing](../paper-writing/SKILL.md) owns drafting a manuscript from
research evidence; this skill owns the harness in which the author writes.

## Start or resume

1. Find the harness (`harness.toml` under `writing/<paper>/`). If none exists
   and the user wants one, create it with
   `python3 scripts/cards.py init writing/<paper>/harness` and set `language`
   to the author's language. Existing drafts are imported into cards with the
   author's agreement; never overwrite an existing card.
2. Run `check` and `status`. Report errors, `STALE` prose (including text
   whose cited code, run or figure changed; see `evidence` in
   [cards](references/cards.md#evidence-from-code-runs-and-figures-reverse-staleness)), `OUTDATED`
   outputs, forward references and open questions before new work, and any
   new file in `reviews/comments/`.
3. Read `story.md`, `vocab.toml` and `style.toml`, and the workspace's
   `writing/.rules/`. Apply recorded rules without asking again.

## Work

- Follow the four harnesses (story, placement, proof, consistency) and the
  editing loop in [the harnesses](references/harnesses.md). Author-facing text
  uses the language in `harness.toml`.
- Keep the card formats, status ladder, fingerprints and structure rules in
  [cards](references/cards.md). Check [borrowed results](references/cards.md#facts-from-another-harness),
  including those located through a book or lecture. The author's prose lives in explanation cards;
  edit its body only when the author asks.
- When the author names an exemplar paper and asks the prose to follow it, its wording is
  the target, not a soft cue: follow [an exemplar](references/harnesses.md#following-an-exemplar)
  passage by passage, with its phrase table in `style.toml` and `cards.py exemplar` before reporting.
- Run `check` after every change to cards or structure; run `impact` before
  changing a statement and tell the author which prose to reread.
- Every rule learned from an edit is stated, applied paper-wide as a diff after
  approval and recorded at its owner (field, author or this paper). A rule constrains
  structure, such as the order of a proof, the quantifiers or the placement of a lemma; a
  `PHRASE` check only catches typical wording. Reread each fixed passage against the rule's
  intent before reporting it fixed, and never count a rewording that silences the check as
  a fix.
- `cards.py load` lists indicators of how heavy each proof is to read (named
  symbols and their uses, invoked theorems, symbols named before they are
  needed); use it to choose which proofs to reread, not as a verdict.
- Lean: link declarations in `lean:`; raise a card to `lean` only when its own
  objects and statement are formalized.
- Keep every output current: after any change to cards or structure run
  `cards.py build` (check, TeX, PDF, card viewer, reading page in one go), or
  rely on the editing hook, `watch` or the editor, and treat `OUTDATED` from
  `check` like `STALE`. Never tell the author a change is visible before the
  build that contains it has succeeded. See
  [outputs and the editor](references/outputs-and-editor.md).
- The author can edit cards directly in `cards.py serve` (reading page with
  edit links, live reload, comments saved to `reviews/comments/`). Read new
  comment files at the start of each turn; reread fact cards the author changed
  and apply the status ladder.
- New cards come from templates: `cards.py new KIND ID` (harness `templates/`
  override the skill's `assets/card-templates/`).
- Carry the same writing workflow through self-check, review, triage and recheck. Before handing a part to the
  author as a paper, run a [review round](references/review-loop.md) on a frozen copy. Independent reviewers give
  findings in fresh contexts. Integrate accepted repairs within the author's existing editing permissions.

Commit each accepted change in the workspace. Mathematics, prose and review
records of a real paper stay in the workspace, never in this skill.
