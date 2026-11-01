# Optional staged first-reader sessions

Contents: [reader boundary](#reader-boundary) ·
[explicit commands](#explicit-commands) ·
[failure and evidence limits](#failure-and-evidence-limits).

Use only when the user explicitly opts into staged reading. Normal `paper map`
and `paper section` remain complete-opening/complete-section tools. This workflow
does not start a review, request source edits, promote evidence, or repeat reviews
automatically. Apply the [numbered standards](standards.md), especially P3.6 and
P7.6, to the actual reading and report.

## Reader boundary

A coordinator creates the session and controls exposure. Give an isolated reader
only a neutral audience/scope brief and the returned `text` prefix. Withhold the
source path, the session file, filesystem access to them, full-text tools, later
headings, research plans, intended answers, prior findings and author identity
when blind reading is requested. Do not run `paper map` or `paper section` in
that reader's context first. A line boundary need not be a TeX paragraph: choose
an explicit cumulative boundary, without presuming TeX macro expansion.

`independent` is a declaration by the coordinator, not an isolation check or a
fresh-context certificate. If the same context has already seen the paper, call
the result a single-context/local reading. The tool guarantees staged output,
not a filesystem sandbox or another agent's actual knowledge. Session permissions
are restrictive where the operating system supports them, but are not an access
boundary against a reader running as the same user.

## Explicit commands

Resolve `<labo-script>` and select the private workspace as directed by the
owning [skill](../SKILL.md). Paths below are normalized workspace-relative POSIX
paths; the existing parent of the private session must already exist. Never put
a private source or session in the policy checkout. Each command accepts
`--workspace /absolute/private/workspace` and `--format text|json`.

```sh
python3 <labo-script> paper reading start --source writing/example/sections/01-introduction.tex --session research/reviews/first-reader.json --reader reader-one --mode independent --format json
python3 <labo-script> paper reading next --session research/reviews/first-reader.json --through-line 8 --format json
python3 <labo-script> paper reading observe --session research/reviews/first-reader.json --understanding 'The visible text asks ...' --confusion 'The first missing relation is ...' --format json
python3 <labo-script> paper reading next --session research/reviews/first-reader.json --through-line 16 --format json
python3 <labo-script> paper reading status --session research/reviews/first-reader.json --format json
```

`start` refuses overwrite and emits no manuscript text. The default mode is
`single-context`. The coordinator binds the exact UTF-8 source bytes and file
identity internally; it does not preload the full source into the reader.
`next` returns exactly the growing cumulative source prefix, preserving line
endings, and records its hash. Boundaries are one-based source lines, must
strictly increase, and cannot pass the source end. There is no arbitrary range
or skipping ahead to a later-only excerpt.

After **every** exposure, record both the reader's initial understanding and
first confusion before requesting another exposure. If there is no confusion,
say so explicitly; an empty field is not an observation. Do not rewrite that
initial record after seeing later text. Once it is recorded, append reference-
or explanation-assisted recovery separately, for example:

```sh
python3 <labo-script> paper reading observe --session research/reviews/first-reader.json --understanding 'The supplied reference later identifies ...' --confusion 'The original gap is now resolved by ...' --rescue --format json
```

A rescue belongs to the current exposure and requires its initial observation.
It never replaces the first observation. Record any repair suggestions after
the first reader account and label information obtained from references or
author explanations. `status` is read-only and emits boundary/observation counts,
not manuscript text, source paths, total future line counts or observation prose.
The private session itself retains the initial and rescue observations.

## Failure and evidence limits

Every operation checks source identity, exact byte hash, strict session schema,
prefix hashes, and the append-only event chain. Source changes invalidate the
session; there is no automatic refresh. Request a new session explicitly after
agreeing to read the new version. Session files are bounded (4 MiB), sources are
bounded (16 MiB), and malformed UTF-8, duplicate YAML keys, unknown fields,
symlinked paths, workspace escapes and policy-checkout targets are rejected.

Writers use an exclusive adjacent `.lock` and atomic publication. A leftover
lock is not cleared automatically: inspect whether a coordinator is still
active before manually resolving it. Read-only status does not acquire or clear
locks. The hash chain detects accidental or unrecomputed edits, not an adversary
who controls the private session and can recompute hashes; it is not a signed
audit log. Filesystem checks are not protection against a hostile same-user
process racing path replacement. No command edits the source or certifies
mathematical correctness, comprehension, independence, or a whole-paper pass.
