# Synthetic survey reading cases

All names, papers and excerpts below are fictional. These are behavioral
evaluation packets for `reading-reference`, not executable regression tests.
Review each note against its request and supplied evidence. Report supported
findings, the checks actually possible, and what remains to complete the task.
Do not contact external services or invent absent source material.

## Case A: explain two algorithms with corresponding code

Request: Explain the central methods of *Small Graph Procedures: A Survey* in
a self-contained note with executable code. Review the draft for completion.

Survey v1, section 2: The two central methods are Row Average, from Vale (2020),
Algorithm 1, and Pair Exchange, from Reed (2021), Proposition 2 and Algorithm 1.
The historical introduction also lists Moss (1900); it supplies no premise
needed for either method. There are no supplements.

Vale (2020), *Row Average*, supplied full text, Algorithm 1: Given a nonnegative
matrix W with positive row sums d, form P[i,j] = W[i,j]/d[i], and return P @ f.
The output averages neighboring values; P has unit row sums.

Reed (2021), *Pair Exchange*, supplied full text, Proposition 2 and Algorithm 1:
For two scalar values a,b and 0 <= t <= 1, return ((1-t)*a+t*b, t*a+(1-t)*b).
Their sum is conserved, since the coefficients of a and b each sum to one.

Draft note: "Following survey section 2, we implement Row Average below.
Pair Exchange conserves the sum; see our bibliography. Both methods have
been verified. The complete code appendix makes this note reproducible."
The bibliography lists Vale and Reed but gives no locators in the discussion.

The purported Row Average implementation is an independently written function;
its environment and execution are not recorded:

```python
def row_average(W, f):
    return W @ f
```

The sole additional appendix unit is a plotting demonstration of a parabola.
No Pair Exchange code or helper implementing its update is present. The author
reports having executed only the plotting demonstration. No official code
revision is supplied or claimed.

## Case B: required primary source unavailable

Request: Explain the main recovery guarantee of *A Survey of Shape Recovery*,
including its hypotheses and decisive argument. Review the draft for completion.

Survey v2, section 3: "Larch (2022), Theorem 4, gives consistency under suitable
regularity assumptions." This is the survey's central guarantee. The primary
paper's abstract says only that a consistent estimator exists. The full theorem
and proof are inaccessible in this packet. There is no related code request.

Draft note: "The estimator is consistent for every smooth surface. We checked
the abstract and ran a synthetic noise-free example, so source verification is
complete. Reconstructing the primary theorem is outside the scope of this note."

## Case C: theoretical survey without a code request

Request: Explain the two elementary propositions in this theoretical survey.
Review the draft for completion; no computational demonstration is requested.

Survey v1, section 1: Elm (2018), Proposition 1, establishes nonnegativity of a
square. Fir (2019), Proposition 2, applies this to sums of squares. There is no
algorithm, software, experiment or supplement.

Supplied primary texts: Elm, Proposition 1: For real x, x*x >= 0, since either
x >= 0 or -x >= 0, and the product of nonnegative reals is nonnegative. Fir,
Proposition 2: For real x,y, x*x+y*y >= 0, by adding the two inequalities of
Elm, Proposition 1.

Draft note: It states each domain and conclusion, reproduces the given
arguments, and cites Elm (2018), Proposition 1, and Fir (2019), Proposition 2
beside the respective proof, as well as the survey's section. Both supplied
primary texts were inspected. The handoff says precisely this; it makes no
claim to computational or rendering verification. No PDF was requested.
