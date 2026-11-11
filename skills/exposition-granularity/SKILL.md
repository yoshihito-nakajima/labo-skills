---
name: exposition-granularity
description: Estimate, from a corpus of texts by the target community, how much authors define and explain (assumed vocabulary, vocabulary they define, density of definitions and parentheticals), and check a draft or a review against that profile so that exposition is neither under-defined nor padded. Use when drafting or reviewing mathematical exposition for a specific readership, or when reviewers keep demanding definitions of standard terms.
---

# Calibrate how much to explain

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

An adversarial reviewer asked for "every undefined term" will flag standard vocabulary, and a writer who
repairs each flag pads the text. Nothing in that loop pushes back. This skill supplies the counterweight:
a descriptive profile of what the community's own authors define, what they use without comment, and how
dense their definitions are, estimated from a corpus rather than asserted as a rule.

## Scope

- **English prose only.** The profile and its checks describe English texts (`.txt`, `.md`, `.tex`).
  A Japanese deliverable is a literal translation of an English original, made with
  [japanese-translation](../japanese-translation/SKILL.md). Granularity is set and judged on the English
  text; the translation must not add definitions, glosses or parentheticals the original lacks, and must
  not drop any. The script says so when given a mostly CJK text and does not measure it.
- A profile describes the documents it was built from. It is evidence about those authors' habits, in the
  manner of the workspace corpus index, not a rule about what is correct.

## Workflow

1. **Choose the corpus.** Texts from the target community and genre (papers for a paper, abstracts for an
   abstract). At least eight documents; the script refuses fewer than three and labels fewer than eight
   anecdotal. Prefer the author's own samples where voice matters. Keep the private corpus and its
   profile in the workspace; do not copy corpus text into public skill files.
2. **Estimate.** `python3 scripts/granularity.py profile FILE... --out profile.json --report profile.md`
   gives the assumed vocabulary, the vocabulary the authors usually define, and the quartiles of explicit naming phrases ("called", "we say", emphasis markup) and parenthetical remarks per 1000
   words. The naming count misses definitions written as "Let", "Put" or "write", so use it as a rough guide only.
3. **Screen the lists by hand.** Candidates are n-grams after a small stoplist and contain verbs, rhetoric
   and extraction debris. Strike those. Look at the terms the corpus defines every time: a draft that uses
   them must define them. Look at the terms it never defines: a draft that defines them is probably
   padding. Report what you struck so the profile can be audited.
4. **Check the corpus is coherent.** `granularity.py loo FILE...` rebuilds the profile without each document
   and reports whether that document falls inside the others' density range and how often it defines terms
   the others assume. Many outliers mean the corpus mixes genres; split it.
5. **Use it.** A writer consults the screened profile before drafting. A reviewer receives the assumed
   vocabulary as "do not flag as undefined" and the density band as a second finding class,
   *over-explanation* (a definition or gloss of assumed vocabulary, or density above the corpus range),
   reported with the same quote-and-minimal-repair format as the others. `granularity.py check PROFILE ARTIFACT`
   lists definitions of assumed terms, uses of usually-defined terms that stay undefined, and words that occur in no
   corpus document (a gloss that no author in the community needed, such as a word for the object a function class
   represents, shows up here).
   See [interpreting a profile](references/interpreting-a-profile.md).

## Limits to state in every use

The corpus may not match the reader. A small corpus gives noisy lists. A habit of the authors is not
necessarily right for a newcomer reader. Say which of these applies instead of presenting the profile as
a verdict.
