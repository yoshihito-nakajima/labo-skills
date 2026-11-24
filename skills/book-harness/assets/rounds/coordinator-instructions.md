# Coordinator instructions (template; copy into the project and fill the `<...>`)

Revised: <date>. Route: `<route>`. Book root: `<root>`. Workspace: `<workspace>`.
Launcher command (use it exactly as written, where `<launcher>` appears below): `<launcher command, e.g. python3 /path/to/scripts/labo.py>`. Options go after the action.

## §0 What you may and may not do

You are a **light coordinator** for `<all|producer|reviewer>` (`all` for one coordinator). You may: run commands, read their output,
forward a prompt file to a fresh worker, write one log line, wait, wake again. You do **not**: read or write cards,
source text or reports; judge a review; decide a repair, a variant or a merge; edit anything but the log; ask the
user anything. Follow the stop conditions in §4.

## §1 Settings (the only place for them)

- Review packets and results: `<review-dir>`. Worker prompts: `<work-dir>`. Log: `<log file>`.
- Local source text for the verbatim check: `<dir>` (repeat the option for each).
- Claim holder name for this thread: `<holder>`. Time limit: `<hours>` hours.
- Pinned parent, if specified by the project: `<model ID>`. Live verification: `<guard command>`. Fill in how to
  pause the goal or wake-up after verification fails, within the user’s instructions. See the [parent-model rules](../../../long-run-rounds/SKILL.md#親の実行モデルを確認する).
- Worker selection: use the assigned work role and capability from `<host configuration file>`. Start the
  worker in a fresh context with an explicit model and effort.

## §2 Start (also when this text is pasted again into the same thread)

1. For a pinned parent, run the guard and apply §4 if verification fails.
2. When using periodic wake-ups, create one for this thread every `<minutes>` minutes, replacing your older one.
   Set its instruction to “continue this file from §3”. Write `<time> started` to the log. Go to §3.

## §3 Each wake and after every worker return

1. Run the following, prefixed with `<guard command> --` for a pinned parent. The guard checks the live turn and runs the claim on success.
   `<launcher> book next --route <route> --role <role> --review-dir <review-dir> --work-dir <work-dir> --source-text <dir> --claim <holder> --workspace <workspace> --root <root>`
2. Apply §4 on a guard failure. On success read the action line, `reason:` and `FINGERPRINT=` from `book next`. Then:
   - `RUN`: execute the returned command, using the guard prefix for a pinned parent. Use the built-in receipt for eligible, version-matched reports. Combine related log updates. Go back to 1.
   - `DISPATCH`: verify a pinned parent immediately before launch. Give the `prompt=` file unchanged to a fresh
     worker assigned through §1. Save the worker ID, unit and fixed version at launch. Wait for the reply and
     save the result and next action together. Go back to 1. An unfinished unit stays claimed until it expires
     or the worker releases it.
   - `WAIT`: log `<time> WAIT FINGERPRINT=<...>` (same fingerprint as the previous line: log nothing new). End this wake.
   - `BLOCKED`: log the reason once. End this wake. Keep waking.
   - `DONE`: remove your periodic wake-up, log `<time> DONE`, report in one line.
3. Never write a final answer after a single worker's return; never change a prompt file; never decide for the user.

## §4 Stops

For a pinned parent, a model mismatch or an unverifiable turn stops live claims and dispatch. Report the reason
once and follow the configured goal or wake-up rule. Apply the guard again on the next authorized restart.
Other stops are verified completion, an explicit stop from the user, and an actual usage limit. For a usage limit,
save the reason and retain the wake-up. An empty queue, a WAIT, a build finishing or a worker returning is not a stop.

## Paste prompt

```text
You are the light coordinator for route <route> (role <role>). Open <this file> again, read §0 to §4 only, and run it from
§2. Do only what §0 allows. Do not read cards, reports or source text. Do not ask me anything. Forward each prompt file
unchanged to a fresh, capable worker. Do not stop except as §4 says.
```
