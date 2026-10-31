# Workspace style corpus and rules

Use the workspace writing corpus to learn from examples while keeping its
observations distinct from instructions.

## Per-task workflow

1. Identify the manuscript's field, target venue, language, and document type.
2. Read `writing/.rules/README.md` and the applicable rule files. For a
   submission-format task, verify the venue's current official instructions and
   template as well.
3. Read `writing/.corpus/README.md` and its index, then select a small number
   of relevant examples. If the target manuscript has
   `writing/<paper>/decisions/corpus.toml`, use its selected examples and
   judgments as the first guide for that paper. Prefer the author's own prose
   when learning their voice; use field exemplars for genre conventions and
   venue materials for submission requirements. Do not read every corpus item
   when only a few fit the task.
4. Notice recurring tendencies in vocabulary, phrasing, sentence and paragraph
   length, transitions, register, claim framing, and pacing. Treat these as
   weak style cues, not hard constraints. Preserve the author's intent and the
   current request. Learn the pattern rather than reusing distinctive wording,
   sentence sequences, or claims.
5. Check whether the selected examples actually cover the requested style
   choice. Coverage is weak when no source is close in field, language, genre,
   or register; when source versions or locators cannot be checked; or when
   examples materially disagree and the difference has no clear explanation.
   A small corpus alone is not a problem if its examples are relevant and
   trustworthy. Treat coauthored samples as field evidence when an individual's
   voice cannot be isolated.
6. When weak coverage limits the requested style match, warn the user with the
   concrete gap and its effect on the current draft. Explain that a relevant
   source can be added to `writing/.corpus/index.md`. If the user wants a
   repeated preference to govern future drafts, explain the scoped-rule option
   in `writing/.rules/`. Continue the requested work where possible and mark
   style choices that remain tentative.
7. If a task-specific choice is made from examples, record the selected source,
   locator, and resulting judgment in
   `writing/<paper>/decisions/corpus.toml` when that file is part of the
   manuscript's decision record.

## Promoting observations

The corpus remains descriptive. A single example or an uncertain tendency does
not create a rule. When a recurring preference remains unresolved, explain the
gap and, when useful, offer a concise, scoped rule for the user to add to
`writing/.rules/`. Keep its evidence and exceptions with the rule. The user may
also add or revise workspace rules directly.

Add guidance to this skill only when the user or assistant identifies a durable
writing convention that applies across fields. Keep author voice, discipline
conventions, and venue requirements in the workspace corpus or rules, with
their scope stated explicitly.
