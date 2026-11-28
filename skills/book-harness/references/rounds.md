# Running a card route with a light coordinator

Use one light **coordinator** for the route's production, review and repair cycle. It dispatches substantive work
to fresh workers. An independent reviewer receives the fixed scope and permitted evidence in a fresh context
and returns findings to the producer.

The current `labo book next --role all` automates C2-backed production and related review tasks. Assign other
route units from the existing plan using the same [reading loop](reading-loop.md), and confirm closure against
the plan. Use [long-run-rounds](../../long-run-rounds/SKILL.md) for scheduled operation.

## Roles and model capability

| Tier | Does | Never does |
|---|---|---|
| **coordinator** | calls `book next`, runs the `RUN` command, forwards a `DISPATCH` prompt to a fresh worker, relays the worker's last line, waits, wakes again | reads or writes cards, source or reports; judges a review; decides a variant, a merge, a repair; asks the user |
| **worker** | reads the skill and its unit, does the unit in a fresh context, replies in at most three lines | goes beyond its unit; records an independent review itself; talks to the user |

Use the [capability and effort table](../../reading-book/references/token-budget.md#能力の段階と思考量). A light
coordinator handles dispatch and handoffs; scripts handle mechanical checks and builds. Use normal capability
for reading, card writing, route design and ordinary math review, with low effort for routine source comparison,
receipt handling and output review. Assign hard new proofs and their independent verification to upper capability
with high effort. Assign the verification in a fresh context.

Record role-to-model choices in the project's host configuration. Launch each worker with the capability assigned
to its task. If a unit exposes a harder proof obligation, have the worker return its statement and prerequisites
for assignment to the proof role.

## Parent model and per-round cost

When the project pins a parent model, verify the live turn before each live claim or dispatch, including direct
hand-offs outside the automated queue. Use the project's guarded command for live claims and mechanical writes.
See [parent-model verification](../../long-run-rounds/SKILL.md#親の実行モデルを確認する).

- Give the coordinator the next action, unit or packet ID, result path and counts. Keep report contents, full
  diffs and trace logs in files for the worker. Put one receipt in the durable run record per completed unit.
  Keep the dispatch ID and fixed version durable when the unit starts, and combine related writes in one command.
- For a frozen handoff case with a complete no-finding math review, prepare the [machine receipt](review-receipt.md)
  before dispatch and accept it on the independent worker's completion. The receipt emits the preassigned next
  request in one line. Route findings, incomplete returns and version mismatches through ordinary intake.
- While a worker is active, yield to the host's completion notification. Refresh the pointer on completion, a
  substantive change, or the scheduled recovery check for a lost notification or abandoned claim. Repeated
  unchanged waits do not need a model turn, guard, or another log entry. Guard the next live write or dispatch.
- Batch neighbouring exercises or examples with the same direct prerequisites and source scope at a stable
  section boundary. Still require checked IDs and the full independent review of the agreed scope. Split a
  packet that is too large to review in one fresh context, or whose prerequisites are still changing. Check
  output mechanically on the build in use and combine independent visual checks at a stable chapter boundary.
  Check changes affecting the next unit and high-impact reader features on the version that introduces them.
- At a round boundary, use the durable progress pointer to resume after a host-supported context reset if the
  coordinator's context has grown substantially. Track model calls and newly supplied input, cached input and
  output separately, along with completed units and current review coverage.

## The one call

```sh
labo book next --route R --role producer|reviewer|all --review-dir D --work-dir W \
    --source-text TEXTDIR [--source-text ...] --claim HOLDER [--compact | --format json]
```

Use `--role all` for one coordinator. Use `producer` and `reviewer` when intentionally running two coordinators
in parallel. Pass `--claim` for a live run. Without it the call is a dry run. Use `--compact` for a single native-coordinator action line with its fingerprint.
The answer (first line of text output, or the `action` field of JSON) is exactly one of:

| Answer | The coordinator |
|---|---|
| `RUN tier=coordinator command: ...` | runs that command itself, unchanged, then calls `next` again |
| `DISPATCH tier=worker worker_role=R unit=U prompt=FILE` | gives the file `FILE` to a fresh capable worker, waits for its reply, writes one log line, calls `next` again. The unit is claimed |
| `WAIT` | writes `WAIT FINGERPRINT=...` and sleeps until the next wake. A second WAIT with the same fingerprint starts nothing |
| `BLOCKED` | writes the reason; needs configuration or a person; keeps waking (does not invent a fix) |
| `DONE` | the automated source-intake pass is finished: stops its periodic wake and reports |

A worker return continues the round. Apply the completion, parent-model, capacity and user stop rules in the run instructions.

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

With `all`, one coordinator follows the table through both worker roles. The current command selects pending C2
production before ordinary review. Apply the [review timing rules](intake-review.md#when-to-call-an-independent-reviewer)
at stable section boundaries. When a producer reports a proof or serious prerequisite issue that blocks the next
unit, use the existing fixed packet or open a scoped `book review-input --cards` packet and hand it directly to
an independent reviewer. Resume the affected unit once the check clears it or necessary repairs are in. The same
coordinator can arrange
this handoff, and unrelated units can proceed. With two coordinators, each follows its own role's entries.

With `--source-text`, `next` already runs the verbatim check. Give it the text caches for the assigned sources
and use its result for that pass.

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
beside its other run instructions. State the work role and capability in instructions, and resolve the model through
host configuration. Use [long-run-rounds](../../long-run-rounds/SKILL.md)
for capacity stages, status fingerprints and restarts; its status table maps to `book next` and `book status`
(`taken in`, review coverage, STALE ids).
