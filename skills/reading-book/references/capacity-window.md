# Running long unattended rounds within the usage window

Long book and course runs (parent threads that wake on a schedule and hand work to workers) share one account's usage limits. The usual one is the 5-hour window; there is also a weekly limit. A thread cannot read its remaining quota. When a limit is reached, the API answers each request with a synthetic message such as `You've hit your 5-hour limit · resets 7:20am (Asia/Tokyo)` until the reset time. Workers running at that moment stop in the middle of their unit.

## Estimate, calibrate, stage

`scripts/usage_window.py` reads the Claude Code transcripts of all projects, including subagent files. It sums the token usage of assistant messages with rough relative weights (by token type and model) and reports three things: the weighted use in the current 5-hour window, the calibrated limit, and a stage.

- **Calibration.** `--learn --calib <file>` records the weighted sum from a window's start to its first limit message. It does this for each limit message from the last few days. The calibrated limit is the median of the recent observations.
- **Lower bound.** Use on other devices and on claude.ai is not in the transcripts, so the estimate is a lower bound. The limit message remains the ground truth.
- **Project tools.** A project's status tool can call the script and print one line. It should put only the stage (not the number) into any wake-up fingerprint, so that a stage change wakes a waiting parent.

| Stage | Meaning | Behaviour |
|---|---|---|
| 余裕 | below 60% of the calibrated limit | normal work |
| 節約 | 60–80% | only work that unblocks the current target: receive and repair returns, and reviews of the volume being closed. No speculative work (for example, auditing the next volume ahead), no new high-cost model runs (record the request and keep it for later), smaller units |
| 停止前 | from 80% | start no new unit, write the records and wait. The remaining margin is for the user's own sessions and for the director |
| 上限中 | a limit message whose reset has not passed | start nothing. Keep the scheduled wake-up, because the next wake after the reset continues |
| 未較正 | no limit observed yet | work as 余裕 and watch the numbers. The first limit message calibrates the script |

The thresholds are options (`--save`, `--stop`). Raise them only when the user has no other work on the account.

Related tools: [course_driver.py](../scripts/course_driver.py) `usage` estimates the same window for the headless driver and calibrates from readings the user types in; [usage_report.py](../scripts/usage_report.py) breaks usage down by thread and model when looking for causes. `usage_window.py` is for scheduled parent threads (cron-style wake-ups) and calibrates itself from limit messages.

## When a limit is reached

- Do not delete the scheduled wake-up, and do not stop the loop. Record one line with the reset time. Wake-ups before the reset do nothing.
- The first unit after the reset cleans up what the cut left:
  - claims whose results directory is still empty go back to their owner, who either reruns or releases them;
  - a stale model lock is removed;
  - half-written sources must pass the build;
  - published packets missing from the queue are registered.
- Then continue from the recorded cursor.

## Spend less per result

- **Rechecks converge.** Fix minor findings without publishing a new recheck. Publish a new recheck only after a major or medium finding, or once before closing a unit. Close the unit when the latest recheck has no major or medium finding and every minor one is fixed. Successive rechecks that each return only minor findings are the main waste.
- **Work ahead only in 余裕.** Work ahead of the current target (the next volume's audit) is for spare capacity only.
- **Large reviews.** Split large reviews by the reviewer's own budget rather than repeating whole-unit reviews.
