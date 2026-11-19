"""WL-04f false twin — post-mutation cell claimed NOT == v — must stay UNPROVEN.

Soundness oracle for the option-(c) inner-mutation store `a[i][j]=v ~~>
a[i] <- Seq.set a[i] j v`. After the write the cell (i, j) holds EXACTLY `v`, so a claim
that the read-back is DIFFERENT from `v` is false of real Python and must NOT prove. If
this ever PROVES, the functional `Seq.set` update is not being stored back into the
mutable outer array (the write is dropped / mis-modelled) — the lowering is unsound.
Verdict: UNPROVEN."""
_ = 0
from typing import List


#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result != v
def str_inner_mutate_falsetwin(a: List[List[str]], i: int, j: int, v: str) -> str:
    a[i][j] = v
    return a[i][j]
