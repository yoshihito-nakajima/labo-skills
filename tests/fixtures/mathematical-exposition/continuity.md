# Synthetic adjacent-passage continuity packet

All passages are invented for this fixture. Use only the supplied material;
no source lookup, computation or PDF build is needed. For each case, report the
first transition whose purpose cannot be recovered from the adjacent text and
a minimum repair, or explain why the transition works. Do not judge by the number
of headings or by the presence of words such as "therefore". Do not rewrite
protected source titles or quotations.

## A: a code-free explanation

The reader knows finite sets and the triangle inequality. They want to know why
a function f from a nonempty finite metric space (X,d) to the real numbers that
satisfies |f(x)-f(y)| <= d(x,y) has exactly one extension to the completion.
The supplied facts are that finite metric spaces are complete, f extends by
itself, and any extension to X must coincide with f. The draft reads:

> Supplement: bounds
>
> We next study a bound. The function has Lipschitz constant at most one.
>
> Supplement: sequences
>
> We now introduce Cauchy sequences. Every Cauchy sequence in X converges.
>
> Supplement: extension
>
> Below we discuss extensions. The completion is X, so f itself is the unique
> extension.

The statements are supplied as true. The issue to assess is whether the adjacent
prose explains why each topic is needed for the requested result. In particular,
do not insist on retaining all three added units if the target follows directly
from the given completeness fact.

## B: specific headings with detached openings

The preceding paragraph explains that a displayed network has an isolated vertex
and asks whether any path joins it to the marked starting vertex. A supplied
figure shows precisely that network. The next unit is titled "Using reachability
to settle the isolated vertex", but its entire opening is "The following figure
is interesting." After the figure, the prose defines the sum of all edge weights
without connecting that quantity to the reachability question. All figure labels
and definitions are accurate. Assess the text, not just the improved title.

## C: one continuous unit with no extra headings

> The displayed network leaves v with no incident edges. A path from the distinct
> marked vertex u to v would need a last edge incident to v, which the network
> does not contain. Thus v cannot be reached from u. This argument also explains
> why adding edges elsewhere cannot change that conclusion: it supplies no last
> edge into v. Any successful addition must therefore provide such a last edge
> into v as part of a path from u.

The network and distinct vertices u,v are supplied. Assess whether another
heading or a recap before each sentence would improve a missing connection.

## D: comparison whose purpose is not introduced

The preceding unit proves that a procedure returns a defined value for every
input but leaves its accuracy unresolved. The next unit is titled "Comparison"
and begins "Another procedure uses different weights." The rest accurately lists
its weights and cost without stating which unresolved issue the alternative is
being compared on, or whether any accuracy evidence is available. No accuracy
results are supplied. Repair the transition without inventing such results.

## E: source-preservation control

A source section is titled "3 Preliminaries". The user requests a faithful
translation followed by an explanation. The title is accurately translated and
retains its number. Added commentary names the object defined there and explains
how it will be used in the next argument. Evaluate the added prose's continuity;
do not demand a new title for the source itself merely because it is generic.
