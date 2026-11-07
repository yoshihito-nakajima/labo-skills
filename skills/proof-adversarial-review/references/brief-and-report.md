# Common brief and report format

## The brief (write once, give to all)

A short file stating:

- the target: the theorem statement and where the proof is (paths, version, line or label of the
  decisive lemma);
- the rules: do not edit the source; report only; findings carry a location, a severity, a reason and,
  if possible, a counterexample or reproducible computation; separate confirmed from suspected;
  state the scope actually checked; "no gap found" is allowed only with that scope, never "correct";
- tooling: numerical checks may be run (install freely) with working files outside the source tree;
- the expected length of the final report.

Do not include the author's own checks, other reviewers' reports, or the author's opinion of where
the weak point is.

## Report format (each viewpoint returns)

1. A one-line conclusion.
2. The scope checked, listed exactly (files, lemmas, parameter ranges, sources read).
3. Findings, each with: id, location, severity (`fatal`, `major`, `minor`, `form`), status
   (`confirmed`, `suspected`, `unchecked`), reason, evidence for a confirmed one (counterexample or
   command and output), consequence, and the smallest obligation that would resolve it.
4. What was not checked and why (tool limits, unavailable sources).

Severity: `fatal` breaks the stated theorem; `major` leaves a gap, a hypothesis problem or a weakness
in positioning that a referee would require fixed; `minor` is a correctable imprecision; `form` is
exposition or notation.
