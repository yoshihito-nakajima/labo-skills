# Website sources, explanation and release

Apply relevant `W` criteria; report concrete locations, evidence and minimum
repairs. Do not turn a small page correction into a full site audit.

| Intended output | Source basis |
| --- | --- |
| Private explanation | The requested version, including a current draft |
| Public exposition of an existing paper | Identified public preprint, published or archival edition |
| Public topic article | Checked public sources, with added derivations identified |
| Profile, CV or talk page | Verified facts and selected documents appropriate for release |
| Newly released research | The material explicitly selected and authorized for that release |

- **W1 Version fidelity** — Record which edition supports each substantive
  paper claim, with a theorem/section/page locator where useful. Preserve
  differences between editions. A later private proof, stronger theorem or
  improved interpretation cannot silently enter an exposition of the public
  version. A private reader's page does not become public-ready by changing
  its visibility flag. Existing public repository visibility is not blanket
  authorization to publish all files or claims through a site.
- **W2 Source isolation** — If a fresh drafting/review context is needed for
  public-version fidelity, supply only permitted sources, target page and a
  neutral audience brief. Keep private material out of that packet, including
  examples of what not to reveal. Check potential private overlap locally.
  Do not claim source isolation for a context that has seen private drafts;
  record that limitation and perform source-located checks instead.
- **W3 Mathematical explanation** — Make objects, essential hypotheses and
  the useful conclusion understandable before relying on them. Explain the
  decisive relation through prose, equations and examples suited to the reader.
  Separate source results from added intuition or derivation. Verify added
  mathematics; a new lemma or stronger claim is not merely a paraphrase.
  Label theorem, conjecture, observation and analogy accurately. Do not repair
  a source gap by inventing a proof or importing an unpublished result.
  Apply the [readability audit](../../mathematical-exposition/references/reader-pull.md#readability-audit):
  a hurried reader gets result, significance and key idea from the first
  screen; terms are defined before use; the page works with every link removed.
- **W4 Evidence and credit** — Check both sides of historical or novelty
  comparisons. Credit the exact paper and the actual figure/code source;
  distinguish schematic illustrations from measured or reported results.
  Every page that cites works carries an annotated reference list on the
  page, and every numbered or named citation resolves to an entry there (keep
  the source paper's numbers when the text uses them). The page states what
  each cited work contributes: the used result or definition in usable form
  at its point of use, and in the entry what the page takes from the work and
  where (under [reader pull](../../mathematical-exposition/references/reader-pull.md#keep-the-page-self-contained)). Run
  `scripts/check_citations.py PAGE.md --previous-rev REV` on changed pages:
  dangling citations and entries dropped since the previous version are
  defects, whatever the reason for the rewrite.
  Link a paper to an explanation of the matching edition, with differences
  stated when deliberately discussing another version. Inspect rights before
  redistributing source assets; a citation alone does not grant reuse rights.
- **W5 Facts and continuity** — Verify names, affiliations, dates, publication
  status and document targets. Preserve stable URLs and historical publication
  dates; add an update date where appropriate. Redirect intentional URL moves
  using the site's conventions. Do not publish dead placeholder links to
  explanations or files that do not yet exist.
- **W6 Reader and render** — Check the current built page at narrow and wide
  layouts: math/glyphs, diagram labels, captions, overflow, navigation, anchors
  and document links. Keep useful figures beside their interpretation, with
  readable labels and alternative text where supported. A successful build
  does not establish correct rendering or that a reader can follow the argument.
  State unviewed layouts or unavailable previews instead of claiming a pass.
- **W7 Release scope** — Inspect the selected pages, assets and linked files
  before deployment; include generated indexes/feeds if they expose content.
  Keep private inbox material, drafts and private policy out of the release
  unless explicitly selected for publication. Use the user's existing authority
  and destination; if they have not requested publication, prepare a concrete
  candidate first. Never infer publication consent from preparation alone.
- **W8 Operations and reporting** — Use the site's existing generator,
  configuration and deploy mechanism; `loam-ssg` is one optional backend.
  Preserve canonical manuscripts and verification evidence separately from
  derivative web output. Verify deployed pages when publication occurs.
  Report precisely what was drafted, checked, built or deployed, including
  any tool failure or unverified live state; do not equate a local build with
  publication. Site-specific commands do not belong in generic policy.
