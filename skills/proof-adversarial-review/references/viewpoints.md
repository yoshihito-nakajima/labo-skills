# The seven viewpoints

Each viewpoint has one responsibility and its own way of failing. Give every one the common brief
and the source paths, nothing else from the other viewpoints.

| # | role | question | tools |
|---|---|---|---|
| 1 | Line-by-line audit | Does every inequality, index, sign and limit order hold as written? | the producer's hand check; counts as author work |
| 2 | Independent verification | Does a fresh reader, given only the statement and proof, find a gap? | a fresh verifier (see `math-verifier`); often read-only, so it cannot run numerics |
| 3 | Counterexample hunt | Which inputs satisfying the hypotheses break a lemma? Boundary cases, extreme parameters, low-dimensional instances of the whole scheme | a shell with high-precision arithmetic |
| 4 | Hypothesis and dependency audit | Remove each hypothesis in turn: where does the proof break? Is each lemma's hypothesis met at its call sites? Is anything circular? Do the theorem and the end of the proof say the same thing? | reading plus numerics |
| 5 | Prior-art attack | Is the claimed new step already in the listed primary sources? | document retrieval; the source list is fixed in advance |
| 6 | Hostile referee | Reasons to reject: gaps, weakness against what the theorem replaces, significance, positioning, exposition | reading, some numerics |
| 7 | Numerical check | Do the finite identities and inequalities hold on random and extreme data? | a shell |

Notes from use:

- Numerics for sums over a lattice or inverses of triangular systems need high precision; with ordinary
  floating point a stiff case can flip a sign that is true in exact arithmetic. Say which arithmetic was used.
- A hand-check-only verifier is still useful; its report says so, and numerics come from 3, 4, 6 or 7.
- The prior-art viewpoint reports what it read (sections, equations) and what it could not obtain.
  When the closest source is unavailable, that is the finding.
- The hostile referee writes reasons to reject, but each must be defensible and tied to a passage;
  the point is to find the strongest objection, not to manufacture volume.
- Literature a reviewer names from memory is a suspicion until a person reads it.
