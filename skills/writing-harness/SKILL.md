---
name: writing-harness
description: Run an author-led paper harness in which the author writes the prose and the agent keeps the facts — definition and theorem cards with gap-free reference proofs, a status ladder, staleness of prose after a fact changes, reading-order checks, a story ledger with an undefined-term check, a style ledger applied paper-wide, rendering to TeX and a card viewer, and review rounds on frozen parts. Use when the user writes a paper themselves and wants an editor and consistency keeper beside them; for drafting a manuscript from research evidence use paper-writing.
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
2. Run `check` and `status`. Report errors, `STALE` prose, forward references
   and open questions before new work.
3. Read `story.md`, `vocab.toml` and `style.toml`, and the workspace's
   `writing/.rules/`. Apply recorded rules without asking again.

## Work

- Follow the four harnesses (story, placement, proof, consistency) and the
  editing loop in [the harnesses](references/harnesses.md). Author-facing text
  uses the language in `harness.toml`.
- Keep the card formats, status ladder, fingerprints and structure rules in
  [cards](references/cards.md). The author's prose lives in explanation cards;
  edit its body only when the author asks.
- Run `check` after every change to cards or structure; run `impact` before
  changing a statement and tell the author which prose to reread.
- Every rule learned from an edit is stated, applied paper-wide as a diff after
  approval and recorded at its owner (field, author or this paper).
- Lean: link declarations in `lean:`; raise a card to `lean` only when its own
  objects and statement are formalized.
- Render with `render` and build through [labo-build](../labo-build/SKILL.md);
  `html` gives the card viewer; `read` gives the reading page, where the author
  marks passages and copies the comments back to the agent.
- Before handing a part to the author as a paper, run a
  [review round](references/review-loop.md) on a frozen copy.

Commit each accepted change in the workspace. Mathematics, prose and review
records of a real paper stay in the workspace, never in this skill.
