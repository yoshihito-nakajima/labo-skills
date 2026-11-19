# Running the intake with a light coordinator

For long, unattended work a **coordinator** (a small, cheap model, or a person) drives the intake and hands every
piece of mathematics to a **worker**. The design is the table-follower of [long-run-rounds](../../long-run-rounds/SKILL.md),
with the table computed by `labo book next`, so a coordinator never reads cards or judges anything. Nothing here
names a model, a vendor or a host tool: it works with any LLM that can read files and run a command, and by hand.

## Tiers, not models

| Tier | Does | Never does |
|---|---|---|
| **coordinator** | calls `book next`, runs the `RUN` command, forwards a `DISPATCH` prompt to a fresh worker, relays the worker's last line, waits, wakes again | reads or writes cards, source or reports; judges a review; decides a variant, a merge, a repair; asks the user |
| **worker** | reads the skill and its unit, does the unit in a fresh context, replies in at most three lines | goes beyond its unit; records an independent review itself; talks to the user |

A coordinator is a restricted role (evidence collection and relaying): it must not be the one that writes the cards
or judges the review, whatever it could do. Which concrete model fills a tier is host configuration (a project
file), never part of an instruction or a prompt. A worker must be launched with an explicit capable choice, not by
inheriting the coordinator's own.

## The one call

```sh
labo book next --route R --role producer|reviewer|all --review-dir D --work-dir W \
    --source-text TEXTDIR [--source-text ...] --claim HOLDER [--format json]
```

`--role` is the coordinator's job (one thread produces, another reviews; `all` for a single coordinator). `--claim`
must be passed when running for real; without it the call is a dry run. The answer (first line of text output, or the
`action` field of JSON) is exactly one of:

| Answer | The coordinator |
|---|---|
| `RUN tier=coordinator command: ...` | runs that command itself, unchanged, then calls `next` again |
| `DISPATCH tier=worker worker_role=R unit=U prompt=FILE` | gives the file `FILE` to a fresh capable worker, waits for its reply, writes one log line, calls `next` again. The unit is claimed |
| `WAIT` | writes `WAIT FINGERPRINT=...` and sleeps until the next wake. A second WAIT with the same fingerprint starts nothing |
| `BLOCKED` | writes the reason; needs configuration or a person; keeps waking (does not invent a fix) |
| `DONE` | the intake is finished: stops its periodic wake and reports |

Never stop on a single worker's return; stop on `DONE` or an explicit stop by the user.

## What `next` decides (in this order)

1. **A returned review** → `RUN record-review --packet P` (reviewer role). The reviewer's report ends with one line
   `RESULT: pass|findings [CHECKED: id,id|all] [FINDINGS: id,id|none]`; the tool records it only for cards whose fingerprint still matches.
   A report without that line is refused: send it back, do not guess.
2. **Check errors**, **findings of a returned review** (`triage:`), **open findings (D1)**, **verbatim runs** → a
   producer unit. (Producer role.)
3. **Source rows still `TODO`, `MISSING` or `PARTIAL`** → a producer unit `read:<row>`: the reading loop for one row.
4. **Imported (legacy) cards**, **unconfirmed dependency candidates**, **stale cards** → producer units in bounded
   batches (`--batch-chars`). With `--skip-legacy` imported cards are *carried over* as they are (they render as their
   original text, are not restructured and not reviewed here, and `status` counts them separately).
5. **Ready fact cards without a current math review** (split into sections, variant chosen, not stated-only, fresh,
   no check error) → `RUN review-input ...` to make frozen packets in `--review-dir`; then each open packet →
   a reviewer unit `review:<case>/<packet>`. (Reviewer role.)
6. **Nothing to start**: `DONE` only when `taken in` (see [intake review](intake-review.md)) and the verbatim check
   was run and is clean; `BLOCKED` when it is taken in but `--source-text` was not given; otherwise `WAIT`.

Roles split the list: the producer coordinator never gets review work and the reviewer coordinator never gets
production work, so two threads run in parallel. Review waits for the cards it needs to be ready; a producer thread
with nothing left to do waits until the reviews close the batch.

## Claims, packets, results

- A dispatched unit is **claimed** for `--ttl-hours` (default 12); a second coordinator is told `WAIT` instead of
  getting it. The worker releases it (`book release UNIT`) when finished; triage units are released with `--done`.
  An expired claim frees the unit again. State derived from the cards (a row still TODO) needs no done marker.
- A review packet is `<review-dir>/<case>/input/packet-NN/` (frozen, never overwritten). The reviewer writes
  `<review-dir>/<case>/result/packet-NN.md`. A packet whose cards have all changed, or that got no answer within the
  time limit, is void and its cards are offered again.
- The worker prompt is a self-contained Markdown file under `--work-dir`: the unit, the skill's files to read, the
  exact commands (options after the action), the rules, and the reply format. It names no model or tool.

## Realizing DISPATCH on a host

Any mechanism that gives a worker a *fresh context* with the prompt file works:

- a host with sub-agents: start a new sub-agent without the coordinator's history, give it the file's contents, select
  a capable model explicitly (from the project's host configuration), wait for its reply;
- a command-line host: `<llm-cli> < FILE` (or its equivalent), capture the last lines;
- by hand: paste the file into a new session of a capable model and paste the reply back;
- no fresh-context feature: run the unit sequentially in a new session and say so; a review done in the producer's own
  context is not an independent review.

## Where it runs, and what leaves the machine

Cards are course material: run the coordinator and the workers **locally** (the host's own scheduled wake-ups, a
loop in a session, or by hand), not as a scheduled job in someone else's cloud. A worker reads card text and local
source text; if the worker is a hosted model, that text goes to its provider as it does in any other use of that
model, which is the user's existing decision; a locally run model keeps it on the machine. The prompts and the
commands carry paths and ids, not card text.

## Writing the instructions

Use the [coordinator instruction template](../assets/rounds/coordinator-instructions.md) and its paste prompts: sections
for what the coordinator may do, the table above, wake-up and stop rules, and the log line; keep them in the project
beside its other run instructions, never in the skill. Record the host's tier-to-model mapping in a project file and
say "capable worker" and "light coordinator" in the instructions. Use [long-run-rounds](../../long-run-rounds/SKILL.md)
for capacity stages, status fingerprints and restarts; its status table maps to `book next` and `book status`
(`taken in`, review coverage, STALE ids).
