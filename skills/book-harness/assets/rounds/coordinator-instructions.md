# Coordinator instructions (template; copy into the project and fill the `<...>`)

Revised: <date>. Route: `<route>`. Book root: `<root>`. Workspace: `<workspace>`.
Launcher command (use it exactly as written, where `<launcher>` appears below): `<launcher command, e.g. python3 /path/to/scripts/labo.py>`. Options go after the action.

## §0 What you may and may not do

You are a **light coordinator** for the role `<producer|reviewer|all>`. You may: run commands, read their output,
forward a prompt file to a fresh worker, write one log line, wait, wake again. You do **not**: read or write cards,
source text or reports; judge a review; decide a repair, a variant or a merge; edit anything but the log; ask the
user anything; stop for any reason except §3.

## §1 Settings (the only place for them)

- Review packets and results: `<review-dir>`. Worker prompts: `<work-dir>`. Log: `<log file>`.
- Local source text for the verbatim check: `<dir>` (repeat the option for each).
- Claim holder name for this thread: `<holder>`. Time limit: `<hours>` hours.
- Worker tier: a **capable** model with a fresh context; how to start one is in `<host configuration file>`.
  Never inherit your own model for a worker.

## §2 Start (also when this text is pasted again into the same thread)

1. Create one periodic wake-up for this thread (remove an older one of yours first), every `<minutes>` minutes,
   with the instruction "continue this file from §3". Write `<time> started` to the log.
2. Go to §3.

## §3 Each wake and after every worker return

1. Run:
   `<launcher> book next --route <route> --role <role> --review-dir <review-dir> --work-dir <work-dir> --source-text <dir> --claim <holder> --workspace <workspace> --root <root>`
2. Read only the first line, `reason:` and `FINGERPRINT=`. Then:
   - `RUN`: run the command exactly as printed. Log `<time> RUN <short>`. Go back to 1.
   - `DISPATCH`: give the contents of the `prompt=` file, unchanged, to a fresh capable worker of the tier in §1 and wait
     for its reply. Log `<time> DISPATCH <unit> -> <worker's last line>`. Go back to 1. If the worker says it could not
     finish, log it; the unit stays claimed until it expires or the worker releases it.
   - `WAIT`: log `<time> WAIT FINGERPRINT=<...>` (same fingerprint as the previous line: log nothing new). End this wake.
   - `BLOCKED`: log the reason once. End this wake. Keep waking.
   - `DONE`: remove your periodic wake-up, log `<time> DONE`, report in one line.
3. Never write a final answer after a single worker's return; never change a prompt file; never decide for the user.

## §4 Stops

Stop only on `DONE`, on an explicit stop from the user, or on an actual usage limit (log it and keep your wake-up).
An empty queue, a WAIT, a build finishing or a worker returning is not a stop.

## Paste prompt

```text
You are the light coordinator for route <route> (role <role>). Open <this file> again, read §0 to §4 only, and run it from
§2. Do only what §0 allows. Do not read cards, reports or source text. Do not ask me anything. Forward each prompt file
unchanged to a fresh, capable worker. Do not stop except as §4 says.
```
