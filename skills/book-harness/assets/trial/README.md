# Trial kit: does a fresh agent follow the skill?

A fictional source (`source/excerpt.txt`, a one-page chapter on parity) with a planted error (Proposition 2.3 claims
the product of two odd numbers is even and "proves" it with a gesture) and a sketch-level proof.

To run a trial give a fresh agent only this skill and the excerpt, an empty scratch book root and the task "take
Chapter 2, pages 14-15, into the pool as route `toy-parity`, with the intake review up to the packet". Then run

```sh
python3 skills/book-harness/scripts/trial_check.py --root <scratch root> --route toy-parity --source-id src-toy \
    --source-text skills/book-harness/assets/trial/source
```

It checks the mechanical evidence (no check errors, source mapping rows with locators, fact cards created through the
pool search, no legacy cards, proof steps cited, no verbatim run, a review packet bound to current fingerprints) and
lists what only a reader can judge: whether the planted error was corrected and recorded in a `difference`, whether the
exercise was restated, whether the boundary case `n = 0` was treated, and whether the report separates what was and
was not independently reviewed. The fictional text is safe to publish; do not put real sources here.
