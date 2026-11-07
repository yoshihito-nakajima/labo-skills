# Code pages

Showing code is only useful if the page says where to look and what is characteristic.
A listing without that is a decoration.

## Computation and code on one page

When the algorithm's steps and the code fit together at the minimum text size of
[design rules](design-rules.md) (as a guide, up to about five steps and fifteen lines), use one page:
the steps on the left, each with its reason and source, the code on the right, and each code mark
labelled with the step number it implements. Otherwise use two pages, the algorithm page first,
and keep the code marks labelled with the same step numbers. Each code excerpt carries the reason
card of [application to code](../../reading-reference/references/application-to-code.md): the step,
the reason with its source, the lines to look at with their roles, and the provenance.

## Anatomy of a code page

- **Title**: what the code does or what its characteristic feature is, as a claim. Never
  a line count (code changes; a number typed into a title becomes false).
- **Subtitle**: input and output in one line.
- **Idea recap**: the subtitle or a strip above the code states the idea of the subsection
  in one line (what is replaced in what), so the code is read against it.
- **Code**, left, about 60 percent of the width: the whole function (or one coherent
  step), line numbers on, a small numbered marker after each line the audience should
  look at, whose style gives its role: fix, aim, inherited, forward; tidy lines are dimmed
  (`scripts/extract_code.py --mark LINE:N:TEXT:ROLE`; see
  [roles](inherit-new-forward.md)).
- **Look at**, right: three or four numbered items, each `role + lines + what it does +
  where the idea appears`, in the audience's language, at most about three short lines each.
  The `fix` items come first and say which obstacle they remove; an `aim` item says its purpose;
  an `inherited` item says what is kept; a `forward` item says what leads to the next subsection.
  Use `\begin{lookat}\lookitemr{fix}{1}{L5--6}{...}...\end{lookat}`.
  Roles that do not occur are not invented.
- **Provenance tag** (bottom): who wrote the code, that it is not the source authors'
  code, the file and line range, and whether it runs and how that was checked.
- **Closing bar**: one sentence.

Items must be checkable against the lines they cite. Where the code differs from the
source (for example the source's neighborhood includes the point itself and the code
excludes it), say so in an item instead of leaving the difference to be discovered.

## Whose code

The order of whose code is shown is the one of
[reading-reference](../../reading-reference/references/application-to-code.md#show-the-adopted-source-code-first),
and the extent shown follows its license table (R6a of the same skill's source rules). Prefer, in this order: the authors' published code (an excerpt shown verbatim, with the
authors' own comments, credited as authors, repository and file, line range, commit and
license status; if no license is stated, say so and keep the excerpt short); another
published implementation named in the source; and only if neither exists, code written
for the talk. Code written for the talk is kept minimal, adjusted only for clarity,
and labelled. The same order applies to figures and numerical results: take them from
the source and the cited originals before making any.

## Wording about who wrote what

The provenance classes are fixed in [sources, R5a](../../reading-reference/references/source-rules.md);
this section is only how a slide shows them. Run the same
`provenance_lint.py` of [reading-reference](../../reading-reference/scripts/provenance_lint.py)
over the deck sources before release. Code written by an AI assistant must not read as the speaker's own work. Do not write
"own", "our", "my" or "自前" for code, experiments run with that code, or figures made
from it. Write, for example, `Code: written by AI (Claude) from the algorithm of the
survey; not the authors' code` and label figures and numbers `supplementary
experiment (AI-written code), not in the paper`. Say what the speaker actually did
(checked, ran, selected) only when that is true.

## Numbers and claims on a code page

Any quantity about the code or its output (lines, iterations, errors) is measured by
running it or omitted. Do not hand-type counts into titles. State line ranges only in
the source tag, taken from `extract_code.py`'s report.

## Both decks

The reading deck and the stage deck carry the same code pages (one shared source for
the frame, two styles). The stage deck's pipeline page precedes the code page and
names the lines of the code page that implement each box.

## Length

A page carries one function or one coherent step. If it does not fit at the minimum
code size of [design rules](design-rules.md), split by feature, not by line count: one
page per characteristic feature of the method (for example, the kernel and normalization on
one page and the update rule on the next), each with its own idea recap, "look at" list and
step numbers, and no truncated middle. A page is also split when two excerpts show different
features, even if they would fit together. Say in each page's closing bar which feature the
next page shows.
