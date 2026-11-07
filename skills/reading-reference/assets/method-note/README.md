# Method-note skeleton

A starting point for a detailed reading note of a method-and-code paper
([profile](../../references/method-paper-profile.md)). All content here is fictional
placeholder text; replace it. Nothing in it comes from a real paper.

| File | Use |
|---|---|
| `macros.tex` | shared macros: source and added-material tags, role headings, original/translation environments, background card, figure and author-code listing, unit-chain box. Set `\NoteDir` and `\PDFURL`; labels are defined once and can be translated. |
| `main.tex` | skeleton root: scope, spine and section map, one worked source unit (card, original, translation, correspondence, code), supplement, status, bibliography. Build with the workspace's TeX build (`labo-build`), LuaLaTeX. |
| `intake.json` | fictional intake record: the supplement, cited works and substitutes with places tried; `scripts/check_intake.py` checks it and prints the proposal table. |
| `coverage_spec.json` | skeleton of the coverage data read by `scripts/check_coverage.py` (resources, comparisons, units, sentences). It passes the gate as shipped; keep it passing as the note grows. |

The skeleton holds places for the parts a companion page takes over (lineage overview, values,
code-block notes, figure differences); `coverage_spec.json` records them under `overview` and
`scripts/check_coverage.py` checks that they are present.

Rules the skeleton does not repeat: obtain and report sources and supplements, and never
fill a missing resource with an AI-created stand-in without the user's permission for that
resource ([ledger](../../references/resource-ledger.md#when-something-cannot-be-obtained)); label
every run, figure and code unit by provenance (R5a in [Sources](../../references/source-rules.md)).
