# Literature intake: from the paper to a proposal, to what the user supplies

Use at the start of a detailed reading note (and of a companion page built from it), when the
paper cites works, supplements, code or data that the explanation depends on. It joins three
things the note's other parts own separately: the [lineage inventory](lineage-and-comparison.md),
the [ledger and request list](resource-ledger.md), and the preservation rule R6 of
[Sources](source-rules.md). Its product is one record, `intake.json`, and one proposal table the
user reads and answers.

## Policy

- **Depth.** Start from the paper itself: its supplement, then every work it cites for a relation
  that matters (inherited, baseline, criticised, encompassing, origin, prior version) and the code and
  data it names (depth 0 and 1). Go deeper (depth 2 and on) only where a claim cannot be settled
  without the work behind it: take the works the relevant passage of a depth-1 work rests on. Record
  which work led to which (`led_by`). Stop a line when its claim is settled or the user says so.
- **Open sources only.** Fetch only what is openly available from a trustworthy route
  ([routes](#fetch-routes)). A paywalled, login-gated or doubtful source is avoided, not worked
  around: report it and let the user supply it. A copy of unknown provenance, a mirror, or a
  stale portal is a place tried, not a source.
- **Alternatives are asked, never assumed.** When a work cannot be obtained, propose a substitute
  (another version, a review, a related open work) with its reason, and wait for the user's
  confirmation before using it, even when it is free. A confirmed substitute is labelled as such
  wherever it is used.
- **Nothing is invented.** A missing work stays missing, with the places tried.

## Steps

1. **Intake.** Identify the paper and its version; list its supplement items, cited works by relation
   and need (`must`: a claim or a code step of the note rests on it; `useful`; `optional`), the
   repositories and datasets. One entry each in `intake.json`.
2. **Fetch** what is open, by the routes below, recording every place tried and its outcome. Store
   obtained files under [R6](source-rules.md) with an identity record (SHA-256, version, date).
3. **Propose.** `scripts/check_intake.py intake.json --table` prints one table in three groups:
   obtained; what the user is asked to supply (why it is needed, what it unlocks, where it is
   probably available, why it was not fetched); substitutes proposed for confirmation. Give it to the
   user with the review.
4. **Accept.** What the user puts into the workspace (`inbox/`) gets an identity record, is stored
   under R6, and its entry changes to `obtained`; a confirmed substitute becomes
   `alternate-confirmed` with the date. Re-run the check; read the new material in the order of the
   paper and deepen from it.
5. **Hand over** the final table with the note: obtained and read, still open, avoided, substitutes.

## Fetch routes

Tried in this order; a route that fails is recorded and not retried. Dated facts, to be updated.

| Route | Use | Seen (2026-11) |
|---|---|---|
| The paper's own pages: supplementary-information link, repository named in the paper | supplement, code | repositories open; some publisher supplement links need a browser |
| PubMed Central / Europe PMC full text (`.../europepmc/webservices/rest/<PMCID>/fullTextXML`) | open-access papers, with section structure | worked (full text read in full) |
| arXiv | preprints, versions | open |
| bioRxiv / medRxiv | preprints | v1 pages readable; a later version refused (403) |
| Code hosting (GitHub) at a fixed commit | code, wrappers | open; pin the commit, note the licence |
| Publisher article pages | | often redirect to a login step: not followed; report as not read |
| Data portals | | check that the portal is maintained; a stale or unsafe portal is not a source (one flow-cytometry portal had to be given up) |

## Record

`intake.json` (checked by `scripts/check_intake.py`; a fictional example is in
`assets/method-note/intake.json`): per entry `id`, `work`, `kind` (reference, supplement, code,
data, figure), `relation`, `need`, `depth`, `led_by`, `why`, `unlocks`, `access` (open, publisher-login,
paywalled, unsafe, unknown), `status` (obtained, read, needs-user, alternate-proposed,
alternate-confirmed, avoided, unobtained), `tried` (place, outcome), `stored_at`, `identity`, and for
a substitute `alternate` (what, why, free, confirmed_by_user, confirmed_on). The check rejects a
non-open source marked obtained unless the user supplied it, a substitute used without
confirmation, a missing record of places tried, and reports open `must` entries.
