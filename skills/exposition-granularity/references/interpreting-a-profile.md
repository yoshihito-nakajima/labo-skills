# Interpreting a granularity profile

All examples are fictional.

## What the lists mean

- **Assumed** (`docs_using` high, `docs_defining` near zero): the authors expect the reader to know it.
  In a fictional corpus on "tessellated manifolds", the phrase *tessellated manifold* appears in every
  paper and is never introduced. A draft for that readership does not define it, and a reviewer does not
  list it as an undefined term.
- **Defined** (`docs_defining / docs_using` high): the authors introduce it in each paper that uses it. A
  draft that uses *wrenched index* without a definition is probably missing one.
- **In between**: no signal. Decide from the reader brief.

## Reviewer wording

Add to a reviewer's brief, when a screened profile exists:

> Do not report these terms as undefined: (list). Report as *over-explanation* any definition, gloss or
> parenthetical that restates them, and any passage whose definition density exceeds the corpus range.
> Report as undefined only terms that are neither on that list nor defined in the text.

## Density

Quartiles are per 1000 words of the corpus. `check` calls a value above or below the corpus range when it is
beyond 1.5 interquartile ranges from the quartiles. Treat a value outside the range as a prompt to
look, not as a defect: a survey, a talk abstract and a research paper differ.

## When not to use a profile

- Fewer than eight documents, or documents from mixed genres (see the leave-one-out check).
- A reader who is not the corpus's readership (for example, students). Then the corpus says what experts
  assume, which is the wrong baseline; state the brief's own prerequisites instead.
- Non-English texts: see the scope in the skill.
