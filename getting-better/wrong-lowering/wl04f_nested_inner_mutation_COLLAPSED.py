"""WL-04f — NON-int-leaf nested inner mutation `a[i][j] = v` — **FIXED**.

Before the fix: an inner-mutated `List[List[str]]` param lowered to `array (seq string)`
(the read model), but the in-place inner write `a[i][j] = v` had no sound rendering —
the generic subscript-set path coerced the inner `seq string` container to `int` and
Why3 TYPE-failed. The int leaf routed to the mutable built-in `matrix int`, but a
NON-int leaf had NO mutable 2-D built-in, so the mutation was a REJECTED boundary.

After the fix (wrong-lowering-to-fix.md §WL-04f): the OUTER `array` IS mutable, so the
write lowers to an outer-array store of a FUNCTIONALLY-updated inner seq (option c):

    a[i][j] = v   ~~>   a[i] <- Seq.set a[i] j v

The inner `seq` stays PURE/immutable (`array (array τ)` is Why3 TYPE-rejected). The read
`a[i][j]` is `Seq.get a[i] j`, so the write-read-back `(a[i][j] = v; a[i][j]) == v`
PROVES for str/float leaves. SOUND under aliasing: an inner list can be neither bound to
a local (`b = a[i]` type-fails) nor shared across outer slots (`a = [row, row]`
type-fails), so the value-semantics divergence from Python is unobservable. Verdict:
PROVEN. (Gate-B spike spikes/nested-list-inner-mutable-seq.mlw, Valid Alt-Ergo + Z3.)"""
_ = 0
from typing import List


#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == v
def str_inner_mutate(a: List[List[str]], i: int, j: int, v: str) -> str:
    a[i][j] = v
    return a[i][j]


#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ requires 0 <= i2 and i2 < len(a)
#@ requires 0 <= j2 and j2 < len(a[i2])
#@ requires i2 != i or j2 != j
#@ ensures \result == \old(a[i2][j2])
def str_inner_noalias(a: List[List[str]], i: int, j: int,
                      i2: int, j2: int, v: str) -> str:
    a[i][j] = v
    return a[i2][j2]
