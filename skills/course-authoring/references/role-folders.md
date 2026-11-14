# Role folders and review handoffs

Folders are work destinations and restart entrypoints, not running agents or OS
permissions. Create only the project/case requested; do not scaffold an empty
department tree or appoint owners simply because a folder exists.

| Folder | Owner and outcome |
| --- | --- |
| `local/books/<slug>/` | Producer: book-led canonical text, plan, progress, official output |
| `local/topics/<slug>/` | Producer: topic-led canonical text, plan, progress, official output |
| `local/review/<case>/` | Normal reviewer: bounded math/source or output findings |
| `local/hard_review/<case>/` | Hard-review coordinator: independent attacks on fixed claims, adjudicated findings |

Each active project/case has a short `START_HERE.md` naming the role, actual owner
when known, task, next action, inputs, allowed writes, output location and links to
the relevant skill. Keep generic policy in the skill, not copied into every case.
Preserve existing `AGENTS.md`; an optional scoped instruction can point to the
entrypoint but cannot grant writes outside the assigned area. Reading an entrypoint
alone does not start work unless the user's request asks the agent to execute it.

For an adopted multi-book plan, [course-planning](../../course-planning/SKILL.md)
owns architecture and planning entrypoints within the existing course root.
It does not take ownership of mathematical text, review results or official builds.
A planning folder is not a request to start a planner agent or production loop.

For review cases, use this shape as needed:

```text
<case>/
  START_HERE.md       role, owner, restart point and skill links
  brief.md            exact claims/questions, source version, prerequisites, exclusions
  input/              immutable input copies and content-hash manifest
  reports/            individual reports when there are multiple reviewers
  report.md           bounded normal report or adjudicated hard-review report
  evidence/           only evidence actually needed
```

The brief identifies the canonical producer and return destination, fixes exact
claims/proofs, permitted sources, dependencies, review scope and version/hash.
Review input can include local original extracts, which remain ignored and must
never enter any Git. Keep author commentary and other reviewers' verdicts out of
independent reviewer inputs. Hard-review viewpoints follow the existing adversarial
skill; do not duplicate a second panel procedure here.

Normal review retains exact hypotheses, boundary tests and proof checking, with
fewer selected targets. Hard review adds independent multi-viewpoint attacks;
neither produces a universal certification. Reviewer writes are limited to its
case. It does not repair canonical text, build official outputs or maintain producer
progress. The producer receives, adjudicates/applies, repairs, requests targeted
recheck and updates PDF. No second editable canonical text is created.

Track case state in the existing entrypoint/report and author integration in the
producer's existing progress, linked to one another. Do not create a duplicate
global completion ledger. Returned/READY is not author-received, repaired or
whole-document reviewed. Do not repeat unchanged reviewed questions as new work.
New versions are new immutable inputs/case IDs; preserve prior reports and append
corrections. Retain the legacy `notes/reviews/requests` and `results` layout for
ongoing courses; new folder conventions do not authorize migration or takeover.
