# Survey-paper profile (section-record note)

For a survey or review whose value is in its sections (what each one asks, answers, hands on),
not in one method with one codebase. The [method-paper profile](method-paper-profile.md) fits
a paper with a main method and main-text figures; use this profile when many methods, figures
and code sources are spread over sections. Mixed papers use both: the section record below is
the spine, and a method unit follows the method-paper profile.

## One record per section, one source for every output

Keep a single data file (JSON or Python) with one record per section, including headings that
have no body text. The PDF and the HTML are both generated from it, so section heads, lists and
ledgers cannot disagree. Fields:

| Field | Content |
|---|---|
| id, title, parent, pages | the paper's numbering and printed pages |
| question, answer, evidence | what the section asks, claims, and rests on; each with a page locator |
| selling point | the one thing a reader should carry away |
| weights | (math, code, figures), 0–3; the format is common, only the weights differ |
| lead, bridge | paragraphs for how the section follows from the previous one and what it hands on |
| glossary | terms of the section: plain explanation and what the term is good for, where, field |
| figures, code, materials | references; a material has a state (held, alternative only, requested, paid, not applicable) |

Edges between sections (what a section hands on) live in **one list** `(from, to, what)`; each
section's "receives" and "hands on" are derived from it. State in `what` the thing passed
(an object, a definition, a result), never the target's name. Edges between a section and its own
ancestor or descendant are structure, not hand-offs, and are shown as position instead.

## Verify against the source before output

A record field is a claim about the paper. Check each against the page it cites:

- Figure colour legends, panel contents and datasets are read from the figure image and its
  caption, never inferred; record `color_checked`. If the caption gives no legend, say so.
- Names of categories, symbols and parameters are the paper's own; do not import a term from a
  cited work or from memory (a parameter the paper never mentions is not added).
- Page ranges follow where the heading and the text actually are; a figure placed away from its
  section keeps its true page, with the section that discusses it recorded separately.
- Counting claims (three paradigms, five topics) are recounted from the source.

## Code per section

Every section that has code gets a flow paragraph, its **Steps** (each read line by line, with the specification of the functions it calls), an account of what the result means, and, when a predecessor exists, a comparison card
([comparison](../../reading-companion/references/comparison.md)); a section without a
predecessor says "no comparison" with the reason and still gives its Steps. Original, author or
official code is the main code. AI-written code is allowed only where no original can be
obtained and the user has permitted it for that resource; it is labelled as a stand-in, recorded
in the request list, and always divided into Steps. Do not display code whose licence is unclear;
run it and say so.

## Checks

`reading-companion/scripts/check_section_record.py` checks the record: edges resolve and carry a
substantive label, figures are used and colour-checked, evidence carries page locators, every code
section has Steps and a comparison or a reasoned "no comparison", stand-in code is labelled.
