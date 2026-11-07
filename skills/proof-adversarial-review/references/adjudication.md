# Adjudication by the parent

The parent merges, rules and reports; it does not suppress or soften findings.

- **Merge duplicates** by passage and claim. Keep every viewpoint that raised one; independent
  agreement is information, one voice is not.
- **Confirmed** needs a counterexample or a reproducible calculation, and the parent checks that the
  evidence matches the exact statement. **Suspected** is reasoning only. A reviewer's repair does not
  turn a suspicion into a refutation, and the ability to imagine a repair does not make a gap a pass.
- **Conflicting suspicions** (one reviewer says a hypothesis can be weakened, another that it
  cannot) stay as suspicions with both reasons; do not pick one without a check.
- Where the parent can settle a point quickly by reading the source (a statement missing from the
  theorem, a title that overclaims), it says so in a `ruling`; otherwise it leaves the point open.
- Keep a **panel table**: viewpoint, who ran it, scope actually covered, result. A viewpoint that
  could not run something says so.
- **Stop** when a round raises no new confirmed finding; at most three rounds.
- The parent never edits the source. Suggested corrections go to the author as a list.
- Findings of real work stay in the project's private workspace; this skill's examples are fictional.

`scripts/findings.py` validates the shape (a confirmed finding needs evidence; severities and
statuses are fixed words), merges several reports by id, and prints a count by severity and status.
