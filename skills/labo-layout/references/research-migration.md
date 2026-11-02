# Resume research in the current layout

Use this procedure when the user asks for plan edits or mathematical exploration
in an existing program. Adding the current structure is part of the authorized
research work. Apply it to the selected program, not every directory in the
workspace. Inventory, explanations, report-only reviews and checks stay read-only.

1. Inspect the target's `plan.md`, relevant paths and the work requested. Preserve
   existing plan/evidence/source bytes, links, claim IDs and proof statuses.
   New programs have `plan.md`, `inbox/` and `exploration/tree.json` with a
   supported `schema_version`; absence of a tree in existing research means
   simply that it has not been created. Add a missing `inbox/` when actual
   source intake needs it rather than filling empty legacy directories as setup.
   It is not a finding of research noncompliance, missing proof or failed review.
2. If the tree exists, read `research exploration tree --research <slug>` to
   validate its structure and reuse its nodes/settings. For a missing tree use
   the existing initializer, resolved from the loaded policy checkout:

   ```sh
   python3 <labo-script> research exploration init --research <slug> --if-missing
   ```

   This creates the same empty sequential tree as `layout new research`.
   `--if-missing` validates and returns an existing tree under the same process
   lock without overwriting nodes or settings, including a concurrent creator's
   work. Settings supplied on that call apply only when creating a missing tree;
   use `configure` for deliberate changes. Repeating this step is safe. Invalid
   existing metadata remains in place for diagnosis rather than replacement.
3. Use [research-exploration](../../research-exploration/SKILL.md) for the actual
   investigation. Read nodes before adding; reuse a stable ID for an already
   represented task. Add only the current scoped task when work starts, based
   on the user's request and evidence. Pure plan bookkeeping may leave an empty
   tree. Do not invent a taxonomy, turn every catalog entry into a node or infer
   completed work from old prose. Reuse exact `claim_refs` when present; create
   `claims.yaml` only when there are concrete claims to register.
4. Continue the authorized research work and run the relevant checks. Report the
   structural additions and remaining evidence/formalization work separately.
   `research check` still checks plan frontmatter only. `research exploration
   check` checks the selected tree and recorded formal-evidence freshness;
   new proof-bearing work uses the Lean completion gate. Migration itself never
   upgrades or downgrades past claim statuses or mathematical conclusions.

Tree creation uses the existing native process lock and atomic JSON writer.
If creation fails, preserve the original material and any new plan/inbox files;
inspect the paths actually present and report the missing tree as remaining work.
The new-program command reports this partial outcome explicitly. Retry the
initializer after resolving the cause; never overwrite the program with
`layout new research` or replace an existing tree to recover. The initializer
creates neither nodes nor evidence, so rerunning it cannot duplicate them.

No `research_style` field, compatibility-failure status, bulk migration command,
background service or automatic legacy formalization is needed. The checked-out
layout and the tree's versioned structure are the convention. Parallel mode is
a separate execution choice; existing settings do not broaden authorization or
start agents automatically.
