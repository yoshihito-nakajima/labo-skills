# Outputs in step with the cards, and the card editor

The author reads the paper as a PDF, as the card viewer and as the reading page.
All three are generated from the cards; none is edited by hand. This reference
keeps them current and gives the author a page to edit cards directly.

## One build for every output

```
python3 <skill>/scripts/cards.py build [--no-pdf]
```

runs, in order: `check` (any error stops the build and leaves the old outputs),
`render` for each TeX target, the PDF of each target, `html` and `read`. Use it
instead of the separate commands whenever a card, `structure.yaml`,
`harness.toml`, the preamble, macros or bibliography changed.

Settings in `harness.toml`:

```
[build]
tex = ["cards.tex"]          # TeX targets under paper_dir; {out = "part1.tex", sections = 3} for a part
# pdf = false                # TeX and pages only
# pdf_command = ["latexmk", "-pdf", "{tex}"]   # placeholders {tex} {python} {labo} {harness}
# quiet = 3                  # seconds without edits before a background build starts
# hook_pdf = true            # false: the editing hook rebuilds TeX and pages, not PDFs
```

Without `pdf_command`, a labo-skills checkout builds each target through
`labo.py output build --source <tex>` (engine from the `% !TeX program` line,
output under `output/` with SyncTeX). Without a builder the PDF step is skipped
and says so.

## Seeing a forgotten rebuild

Every output records the hash of the sources it was made from in
`<paper_dir>/.build.json`. `check` reports `OUTDATED <output>` when the sources
changed after that output was made, or when its last build failed; `status`
prints one summary line. Treat OUTDATED like STALE: rebuild before telling the
author a change is visible.

## Building without being asked

- **Editing hook (Claude Code).** `cards.py hook` reads a PostToolUse event on
  stdin. When the written file is a source of some harness it marks that
  harness dirty and starts a detached builder; other files are ignored, so the
  hook is safe project-wide. Add `assets/claude-hook.json` to the project's
  `.claude/settings.local.json` (or `settings.json`). The hook sees only edits
  made through Claude Code's own file tools.
- **Watch.** `cards.py watch` polls the sources once a second and starts the
  same builder; it covers edits from any editor or agent (Codex workers, the
  author's editor, `git pull`).
- **Editor saves** (below) start the builder too.

The builder holds a lock (one per harness), waits `quiet` seconds after the
last edit, builds, and builds again if the sources changed meanwhile. Its log is
`<paper_dir>/.build.log`. A burst of edits therefore costs one build.

## The card editor

```
python3 <skill>/scripts/cards.py serve [--port 8765] [--host 127.0.0.1] [--no-pdf] [--no-build]
```

prints a URL with a one-time token. Pages:

- `/`: the reading page built from the current cards. Each card id is an edit
  link; the bar shows whether the outputs are up to date (hover for the log).
  After any change to the sources the page reloads at the same scroll
  position, or offers a reload button while the author is writing a comment.
  Comments can still be copied, and also saved: they are appended to
  `reviews/comments/<date>.md` in the harness for the agent to read.
- `/cards`: every card with its paper number, title, status, section and
  warnings, a filter, and a form for a new card from the template.
- `/edit/<id>`: the card file in a text area beside a MathJax preview that
  follows typing, the check messages for this card, and its impact (dependent
  facts, prose to reread). `Ctrl+S` saves. A STALE explanation card offers
  "reread", which records the current fingerprints (`anchor`).

A save is refused when the file changed on disk after it was opened (an agent
may be editing the same card), when the front matter does not parse, or when
the id would change (renaming touches references; ask the agent). Errors from
`check` do not block the save; they are shown, and the build stops until they
are fixed.

The editor writes only card files, new cards and comment files. Layer rules
still hold: the author edits prose and may edit facts; the agent rereads a fact
card the author changed, lowers its status when the statement changed, and runs
`impact`.

The server is a local tool. Keep the default host; with `--host` it is reachable
by anyone holding the URL. For reading on another device, publish the static
pages (`html_out`) as before.

## Templates

`cards.py new KIND ID [--title T] [--requires A,B] [--explains X,Y]` (also the
form on `/cards`) creates `cards/<def|prop|expl>/<id>.md` from
`assets/card-templates/<lang>/` (`definition`, `proposition` for every proved
kind, `explanation`). A harness overrides any of them with
`templates/<kind>.md` or `templates/proposition.md`. Placeholders: `{id}`,
`{kind}`, `{title}`, `{requires}`, `{explains}`, `{anchors}` (an explanation
card is anchored to the facts it explains at creation). It never overwrites a
card and does not touch `structure.yaml`.

`assets/review-README.md` is the triage page of a [review round](review-loop.md).
