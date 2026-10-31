# Contextual capability tips

Explain useful capabilities when they connect directly to the user's current
work. A tip should help the user decide what to do next or make a recurring
workflow easier.

## When to surface a tip

- A task exposes a concrete evidence or workflow gap that a workspace feature
  can address.
- A currently available skill or tool can materially improve the requested
  result or produce a useful companion artifact.
- A recurring preference can be recorded once in a workspace-owned place and
  applied in later work.

Do not mention a capability only because it exists. Avoid generic catalogs,
repeated reminders during one task, and suggestions that do not change the
current result or a plausible next step. Continue the requested work when the
tip is optional; surface it at the point where it becomes useful or in the
completion summary.

## How to explain it

In one or two sentences, connect:

1. the observed signal or gap;
2. the capability or concrete action available;
3. the expected benefit or limit.

State what the capability can do now and what requires the user's choice.
Mention only capabilities actually available in the current workspace and
session. Do not imply that an optional operation has already happened.

For example, if a requested style has no close corpus examples, explain which
aspect is weakly supported and that a relevant source can be added to
`writing/.corpus/index.md`. If the user wants a recurring preference to govern
later drafts, explain that they can add a scoped rule under `writing/.rules/`.
The source entry supplies evidence; the rule records an adopted preference.

> The corpus has no close examples in this language, so this phrasing choice is
> tentative. A relevant source can be added to `writing/.corpus/index.md`; if
> you want the preference applied consistently, record it in `writing/.rules/`.

For other tasks, use the same pattern: name a concrete benefit, such as a
section map before revision or a PDF/SyncTeX build after manuscript changes,
and briefly point to the relevant workflow. Keep optional suggestions after
the main requested result unless they affect the current plan.
