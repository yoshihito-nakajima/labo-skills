# The viability indicator

A judgment aid, not a score and not a prediction of acceptance. Six axes each carry a level
(`strong`, `mid`, `weak`, `unknown`) and a reason; a verdict is capped by explicit rules, so the page
cannot state more than the evidence allows. `scripts/indicator.py` is the one authority for the
rules; the page builder prints them and refuses a verdict above the cap.

Axes (`key` in the data): `correctness` (evidence that the proof holds), `novelty` (of the key part,
against the sources read), `delta` (difference from the closest prior work), `strength` (of the
theorem against what it replaces), `significance` (applications and importance), `literature`
(completeness of the check).

Facts used by the rules: `review_done`, `fatal_confirmed` (count), `expert_or_formal_check`,
`closest_prior_unread`, `sources_limited`, `delta_stated`, `attack_survived`.

Verdicts: `none`, `needs_work`, `short_or_preprint`, `journal`.

The rules are listed in `indicator.py` (`RULES`). In short: no review means no verdict; a confirmed
fatal finding caps at needs-work; correctness stays at most mid without an expert or formal check;
novelty stays at most mid while the closest prior work is unread; a limited source list caps the
literature axis at mid; the higher verdicts need a concretely stated difference, and for a journal
a strong novelty, adequate theorem strength and a prior-work attack that did not break the claim.

Always add the list of **what would change the verdict** (`changers`): the specific reads,
corrections, examples or checks that would raise an axis. State on the page that the indicator
aids judgment and certifies nothing.
