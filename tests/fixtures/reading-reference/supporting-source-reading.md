# Synthetic supporting-literature authoring and review packet

All works and passages here are fictional and supplied for unrestricted use in
this trial. Do not browse or infer other source access. Use reading-reference
and its relevant references for the bounded tasks below. Do not edit a real
manuscript, produce a PDF, execute code or translate an unseen paper.

## User request and available sources

Prepare the supporting-source portion of Japanese explanatory notes on the
fictional survey *Local observations*, v1, §4 p.8. Its main original/translation
slots already exist. The added explanation develops why a completion rule
defines an output on empty neighborhoods, what its application actually shows,
and how it differs from positive-row normalization. The notes also have a code
collection for lookup/use. Do not add a whole-document reprint.

The following exact passages and their identities are the complete source input.
Equations and terminology introduced here are available to the reader; no
additional surrounding qualification is omitted from this fictional packet.

- Vale, *Positive rows*, v1, §2 p.2, equation (1):
  "For nonnegative weights with positive sum, divide the weighted sum of values
  by the sum of weights." Equation (1) is y_i = sum_j W_ij f_j / s_i,
  where s_i = sum_j W_ij. No value is defined here for s_i = 0.
- Reed, *Completion rule*, v2, §3 p.4, equation (2):
  "On positive rows, we use equation (1). On an empty row, we retain the center
  value. This defines an output for every row; it does not imply an accuracy
  improvement." Equation (2) is y_i = f_i when s_i = 0. Here "empty" means zero
  row sum; f_i is an observed value, not an estimated population mean.
- Pine, *Station study*, v1, §5 p.7:
  "Three stations had no neighbors within the chosen radius. The completion
  rule returned values at these stations. We did not evaluate their prediction
  accuracy separately." The statement reports a study outcome, not a guarantee.
- *Sensor history* is listed for further reading only. No claim in this
  explanation uses it, and its text has not been inspected or supplied.

An inspected code record `release-v2/complete.py`, function `complete`, lines
1–5, corresponds to Reed's two branches. It was not executed. Its source row
and link are correct; the complete file and operational instructions are already
available in the code collection. No program text needs to be generated here.

## Bounded authoring task

Write the short explanatory passage connecting the three substantive sources,
including the original excerpts and faithful Japanese translations needed at
the points where they are used. Keep added explanation distinct. State how the
code collection relates to this passage, and what if anything is required for
the further-reading item. Do not claim numerical validation or reproduce an
experiment. The supplied English may be quoted in full in this synthetic trial.

## Separate review cases

Review these descriptions with located findings and minimum repairs:

1. A draft supplies accurate code citations and Japanese explanatory paraphrase
   but no supporting English or corresponding translations. It claims its main
   survey translation covers all original-reading requirements.
2. A draft quotes Reed exactly but translates its last sentence as
   「これにより、すべての行で精度の改善が保証される。」
3. A draft quotes only "This defines an output for every row" and joins it to
   Pine's first two sentences without identifying the source switch or the
   omitted accuracy qualifications. It calls the combined block a single original.
4. A draft pairs the exact inspected passages with faithful translations and
   locators, but puts all pairs in a distant appendix; the local explanation has
   only code-source links. It requires the reader to assemble the correspondences.
5. Reed v2 becomes inaccessible in another task and only a secondary paraphrase
   is available. The writer translates that paraphrase into English and labels
   it "Reed v2 original", with a confident p.4 locator.
6. All passages and translations are correct, but each heading says only
   "Original". Vale, Reed and Pine are alternated, with their identities present
   only in a final bibliography. Links labelled "source" and "here" point to
   the correct works. Assess whether correct destinations resolve the ambiguity.
7. Reed's three sentences are split into three original/translation mini-blocks,
   each followed by the same paper, bibliography and code links. No words or
   qualifications are missing, but the positive branch, empty branch and scope
   qualification no longer read as one rule. Propose a coherent unit and clear
   source/action labels without requiring longer quotations by quota.
8. In a further fictional passage, the source says "We define the completed
   value by the following rule:" and immediately gives equation (2) and its
   zero-row condition. The draft quotes only that introductory sentence, puts
   a link on the word "rule", and displays a different explanatory formula
   elsewhere. Assess whether the original/translation unit is complete.

As a control, Reed's complete three-sentence passage and its faithful translation
share one heading naming Reed, the work, version and locator. Inside that unit
the labels are simply "Original" and "Faithful translation", with one descriptive
source link at the boundary. Decide whether attribution must be repeated at
every sentence, or whether this already provides an identifiable reading unit.

## Scope controls

A different user asks only for a two-sentence Japanese translation of supplied
text. Another wants a bibliography index without explanatory prose. State whether
either task requires the full explanatory workflow or passage pairs from every
cited work. Do not turn these controls into full deliverables.
