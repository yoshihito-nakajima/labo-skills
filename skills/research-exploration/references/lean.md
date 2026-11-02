# Lean placement and proof completion

The user's policy for the current exploration workflow is that every proof receives Lean
assurance. Keep projects under `lean/<environment-or-program>/`, sharing one
toolchain/dependency environment when appropriate, with small modules for topics
and results. Prefer this over a separate Lake project per node. Reuse existing
projects and module boundaries; do not move legacy Lean or formalize all old
programs as setup. Research nodes reference the existing `claims.yaml` index
with exact `formal.project`, `formal.source`, fully qualified declaration and
kernel/alignment reports. Avoid a competing theorem index in the tree.

The current evidence fingerprints cover every `.lean` file in the mapped
project plus its environment files. Adding even an unrelated module in a shared
project can stale other claims' reviews. Group related exploration changes
before renewing formal reviews; consider separate projects when change frequency
and reuse boundaries differ substantially. A done task with stale records stays
recorded as done but needs rechecking and is excluded from current record
coverage. Rehashing a snapshot alone never renews a substantive assessment.

This applies to every independent mathematical conclusion, not just theorem /
lemma labels: examples, counterexamples, definitions with asserted properties,
questions settled by proof and separately reused helper propositions also need
claim registration and Lean evidence. Mark such nodes `--proof-required`.
Theorem/lemma nodes always require it. Split a purely organizational task from
its proof obligations when their completion differs. Preserve informal proofs
and literature proofs as evidence while formalization is pending.

Before treating a proof target as finished:

1. State the exact mathematical claim, objects, hypotheses, quantifiers and
   conclusion; index independently reused helper claims too.
2. Actually run the relevant Lean build/check in the prepared environment and
   record the command, toolchain, input scope, output and exit status. Inspect
   the exact declaration's elaborated type and its transitive `#print axioms`.
   Require absence of `sorryAx`; explicitly assess the allowed standard axioms.
   Do not assume the desired theorem itself, or replace its proof by an
   unproved custom axiom or circular bridge hypothesis.
3. Inspect alignment with the mathematical statement: objects, assumptions,
   quantifier order, conventions and conclusion. Kernel acceptance alone cannot
   establish this alignment. Record a substantive alignment report with source
   locations and any trust assumptions.
4. Register the exact mapping and actual nonempty kernel/alignment reports in
   the adopted catalog. Only then use `verified-formally` and create a completed
   directly covering `formal` review using the existing evidence protocol's
   current-input snapshot. A proof/owner review alone does not satisfy this gate.
   Each transitive claim dependency also needs its own directly covering formal
   assessment; a main theorem review does not approve its lemmas transitively.
5. Run `research exploration check --research <slug>` or inspect
   `tree --with-evidence` before declaring the proof task done.

The CLI rejects done proof tasks with no exact claim references, absent claims,
missing mappings, unfinished/failed reports, non-formal claim status, absent
direct formal review, stale inputs, empty reports or bare verdict tokens. It computes record states
separately from work states: `unregistered`, `unformalized`, `execution_pending`,
`alignment_pending`, `review_pending`, `scope_pending`, `stale`, `failed`,
`invalid`, `current_records`. Lightweight tree uses `not_checked`; purely
organizational nodes use `not_required`. These are recorded-evidence states,
not automated mathematical certification. A “pass” string and nonempty report
cannot prove the report truthful: the agent must perform and inspect the work.

The existing selected-source `evidence replay` is optional execution support,
not a whole-Lean-environment build. It does not rebuild every prepared import
and currently cannot replay local path dependencies. Execution unavailable or
unsupported means pending, never success. A separately run trusted build/axiom
audit can supply reports, with precise input scope and a fresh formal review.
For local path packages, that review must explicitly snapshot every transitive
local dependency directory with `--tree`; catalog fingerprints alone cover only
the mapped project. The exploration gate checks these tree snapshots and holds
out-of-workspace/unknown path scopes pending. Prepared external packages still
need substantive environment/trust review; no new universal execution engine
is implied by this skill.

Changes to recorded sources, reports, project pins or captured dependency trees
make the review stale; a formerly done node is retained with a recheck warning
and fails `check`. Metadata-only tree intentionally avoids that filesystem
cost. Freshness inspection may hash many source files and scans only the
referenced catalogs plus the selected program's `reviews/` directory.
Preserve legacy catalog statuses and formats. This completion rule applies to
proof-bearing tasks recorded in the tree; adding the structure itself does not
rewrite previous claims or infer their formalization status.
