# Review round on a rendered part

Use this when a part of the paper (a section range or the whole draft) is ready
for the author to read as a paper. It is the harness-specific record of a
round; the reviewing itself follows [exposition-review](../../exposition-review/SKILL.md)
for prose and [proof-adversarial-review](../../proof-adversarial-review/SKILL.md)
when a decisive proof needs several independent viewpoints.

## 1. Freeze

Render the part (`render --sections N --out part1.tex`), build it, and copy the
TeX and PDF into `reviews/<date>-<part>/` as `<part>-frozen.tex` / `.pdf`.
Record the first 16 hex digits of the TeX file's SHA-256 in the round's
README. Reviewers read only the frozen copy.

## 2. Two independent read-only reviewers

Start both on the same frozen copy, without the other's report and without
the conversation:

- **Cold reader.** Reads as the target reader named in `story.md`. Reports
  where the reader gets lost, undefined or ill-placed notions, wrong
  references, missing goals and rendering defects. Give it the
  [exposition-granularity](../../exposition-granularity/SKILL.md) assumed
  vocabulary when one exists, so standard terms are not flagged.
- **Mathematical critic.** Checks every numbered result against its proof and
  its stated hypotheses: global assumptions declared, estimates supported,
  citations matching the cited statement's hypotheses, edge conventions
  (empty sets, infinite values).

Neither edits the source.

## 3. Triage

Write `reviews/<date>-<part>/README.md`:

```
# Review of <part> (frozen <date>, <file> sha256 prefix <16 hex>)

Reviewers: cold reader (<reader profile>), mathematical critic. Reports: <where they are kept>.

## Triage
| Finding | Source | Severity | Action |
|---|---|---|---|
| A global assumption used by Lemma 2.3 is never declared | both | major | fixed: declared in the notation paragraph (<commit>) |
| Opening paragraph does not state the goal | reader | minor | left to the author (story) |

Verdict after repairs: ...
```

Severity is `error`, `major`, `minor`, `citation` or `cosmetic`. Every finding
gets an action: fixed (with the commit), rejected (with the reason), or left
to the author (story and voice decisions are the author's). Fixes go into the
cards, never into the frozen copy; re-render, and re-review the changed
results when a major finding was repaired. A card reaches `verified` only
when the critic's check of its final form is recorded here.
