"""genexp-erasure-wall R2b: `any`/`all` over a generator expression lowers to a bounded,
iff-specified FOLD, not the unconstrained `any_1 (Array.make 1 0)` oracle.

POSITIVE witness: each function proves a postcondition that is a real statement about the
INPUT. Under the old oracle the result was an arbitrary bool and none of these could be
discharged. See 0937 for the negative twin."""
from typing import List


#@ requires n >= 0 and \length(xs) == n
#@ ensures \result != False ==> (\exists k; 0 <= k and k < n and xs[k] > 10)
#@ assigns \nothing
def has_big(xs: List[int], n: int) -> bool:
    return any(x > 10 for x in xs)


#@ requires n >= 0 and \length(xs) == n
#@ ensures \result != False ==> (\forall k; 0 <= k and k < n ==> xs[k] > 10)
#@ assigns \nothing
def all_big(xs: List[int], n: int) -> bool:
    return all(x > 10 for x in xs)


#@ requires n >= 0 and \length(xs) == n
#@ ensures \result != False ==> (\exists k; 0 <= k and k < n and xs[k] > 10)
#@ assigns \nothing
def has_big_listcomp(xs: List[int], n: int) -> bool:
    # The bracketed form shares the SAME generated fold (deduplicated by spec).
    return any([x > 10 for x in xs])
