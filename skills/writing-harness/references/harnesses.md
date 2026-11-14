# The four harnesses and the editing loop

The author writes the paper as continuous prose. The agent works beside them
as co-editor, consistency keeper and story partner. Cards are the backbone of
identifiers and facts, not the unit of prose: text is not managed sentence by
sentence.

## Language

Every author-facing artifact (story ledger, skeleton, reference proofs, viewer,
questions) is written in the author's own language, or in a language the
author names, recorded as `language` in `harness.toml`. An edition in another
language is a later output step, made with
[japanese-translation](../../japanese-translation/SKILL.md) or by the author.
In Japanese, never type a space between Japanese and Latin letters, digits
or inline math; (u)pLaTeX inserts that spacing itself.

## 1. Story

`story.md` holds the question, the main theorems to present, the order of
telling and what the reader should find interesting. The author writes it;
the agent listens and presses as in [story-interview](../../story-interview/SKILL.md)
and does not supply the line. Keep four parts: decisions (the author's, dated),
the material shelf (cards available, with status), candidate main theorems
(marked as proposals) and open questions.

Every notion in the story is written `[[term]]`. `cards.py terms` classifies
each use against `vocab.toml`: unregistered (no definition anywhere: a
question for the author), name undecided, decided (with its defining card) or
standard. With an [exposition-granularity](../../exposition-granularity/SKILL.md)
profile (`--assumed profile.json` or `assumed_profile`), terms the community's
own authors use without definition are reported as *assumed* rather than
unregistered, so standard vocabulary is not turned into definitions. A term
in `vocab.toml` keeps its recorded status even when the profile assumes it.

A story reader may read `story.md` as a target reader and report what would
interest that reader, where the hook is, what is claimed as new and what would
make them stop. It reports; the story stays the author's
(see [paper-introduction](../../paper-introduction/SKILL.md) for the telling order).

## 2. Placement

The skeleton: definitions and statements in reading order, without proofs
(`structure.yaml`). The agent may fill a first order from the story; the
author rearranges. After every move, `check` reports statements that use a
notion defined later (`FORWARD`), prerequisites never shown (`MISSING`) and
unused facts. Report the breakage of a requested move rather than silently
undoing it. For the reasoning behind section roles use
[paper-structure](../../paper-structure/SKILL.md).

## 3. Proof

For each statement the agent first writes a numbered gap-free reference proof
in the card. The author trims one proof into paper prose; the agent infers
which kinds of steps were removed (routine estimates, standard citations,
symmetric cases, ...) and proposes the same trimming for the other proofs.
Proposals arrive as working-tree diffs the author accepts or rejects hunk by
hunk in their editor or with `git diff`. Record `covers` / `omits` in the
explanation card so the omitted steps stay recoverable. Substantive new proof
work goes to the [math-proof-worker](../../math-proof-worker/SKILL.md) role;
raise a card to `verified` only after an independent check
([math-verifier](../../math-verifier/SKILL.md) or the review loop).

## 4. Consistency

Notation, terms, references, hypotheses and numbering across the whole paper.
Any change to a fact card reports everything it affects: `impact` for
dependent facts and prose, `check` for stale anchors. Renames follow the
terminology audit referenced by [paper-writing](../../paper-writing/SKILL.md).

## The editing loop and the style ledger

1. The author fixes one place in front of the agent.
2. The agent states the fix as a general rule and shows the diff of applying
   it to the rest of the paper.
3. After approval it applies the rule everywhere and commits.

Preferences the agent is unsure about are asked once, briefly; clear ones are
inferred from the edit and confirmed once. Every rule is recorded with its
date and whether it was asked or inferred, at its owner:

| Scope of the rule | Owner |
|---|---|
| holds across the field (statement shape, proof economy, notation habits) | `paper-writing/references/manuscript-conventions.md` in the skill checkout |
| the author's preference, any paper | `writing/.rules/` in the workspace |
| this paper only (a symbol, a convention of its sources) | `style.toml` in the harness |

A rule moved to another owner leaves a one-line pointer in `style.toml` so the
record of when it was asked survives.

## Tooling principle

Everything mechanical is a program (`scripts/cards.py`). The agent's judgment
is used for reading, proposing and explaining; it does not hand-check what a
command can check.
