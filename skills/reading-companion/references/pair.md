# The pair: detailed note (PDF) and companion (HTML)

The note and the companion are built from the same understanding and kept as one pair: the PDF is
the source of truth read front to back, the HTML takes its lineage, values, code-block notes and
figure differences from it ([method-paper profile](../../reading-reference/references/method-paper-profile.md)).
`PAIR.json`, kept beside the note, ties them together so that a change in one is noticed in the other.

```json
{"slug": "...", "paper": "...",
 "note": {"pdf": "path", "source_dir": "path", "coverage": "path", "aux": "path"},
 "companion": {"html": "path", "spec": "path"},
 "intake": "path to intake.json",
 "built": {"note_sha256": "...", "companion_sha256": "...", "date": "..."},
 "not_in_companion": [{"comparison": "C-id", "reason": "..."}],
 "corpus": {"dir": "writing/.corpus/method-pairs/<slug>/<date>"}}
```

`scripts/check_pair.py PAIR.json` checks that
- the files exist and match `built` (`--record` re-records after a rebuild), so a stale pair shows;
- every treated comparison of the note's coverage data (relation inherited, baseline, criticised,
  encompassing, encompassed, prior version, primary read) has a lineage card in the companion
  (`comparisons: [ids]` on the entry) or an entry in `not_in_companion` with its reason;
- every main-text figure with code has a `difference` in the companion, and the note's `overview.differences`
  name the same figures;
- the intake record passes `scripts/check_intake.py`;
- with `--require-corpus`, the corpus copy matches the built files.

## Slides

Slides are taken from the companion, not from the note: see
[decks from one plan](../../deck-from-references/references/two-decks.md). Unit ids for the page tags are
listed by `deck-from-references/scripts/link_companion.py list`.

## Starting and building a pair (provisional)

- `scripts/new_pair.py SLUG --workspace <root> [--paper ...]` creates `reading/SLUG/` (note skeleton, `intake.json`,
  `coverage.json`, `PAIR.json`) and `reading/SLUG-companion/` (an empty spec whose build lists what is still to
  fill). It refuses to run when the parent Git does not ignore `reading/`, or a directory exists.
- `scripts/build_pair.py PAIR.json --workspace <root> [--skip-note]` builds the note PDF, then the companion
  (the PDF's labels and pages come from its aux, so the PDF is first), runs the companion check, the coverage gate
  and the pair check, and records the build. `companion.template` in `PAIR.json` names a project template when the
  paper's drawing needs one.
- What stays per paper: the figure drawing (a plotting block in the template), the run scripts and the spec
  content. What is fixed: the page layout, the checks and the pair record. Both scripts are provisional: refine
  them on the second paper.

## Keeping the pair

`scripts/archive_pair.py PAIR.json --workspace <root>` copies the PDF, the HTML and a snapshot of the sources
(note and companion directories without environments, downloads and build state) into
`writing/.corpus/method-pairs/<slug>/<date>/` with a manifest of hashes. Links are not enough:
`output/` is pruned by the build. The corpus is local only (independent Git, no remote); the script
refuses to run unless the corpus has no remote, never touches the parent repository, and does not
publish. Committing in the corpus is local; nothing is pushed, no pull request is made, and the files
are never copied to a tracked path. Register the pair in the corpus index as a format example of both
outputs.
