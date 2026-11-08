"""Test 0804 — non-int-leaf inner ELEMENT mutation a[i][j]=v reads back (POSITIVE).

wrong-lowering-to-fix.md §WL-04f (nested-inner-mutation). A `List[List[str]]` param
that is IN-PLACE INNER-MUTATED (`a[i][j] = v`) lowers to `array (seq string)` — the
outer `array` is MUTABLE (`array (array τ)` is Why3 TYPE-rejected, so the inner
container MUST stay a PURE/immutable `seq`). The int leaf routes to the mutable
built-in `matrix int` (0802/0803); a NON-int leaf (string/real) has no mutable 2-D
built-in, so the write lowers to an OUTER-array store of a FUNCTIONALLY-updated inner
seq (option c):

    a[i][j] = v   ~~>   a[i] <- Seq.set a[i] j v

`Seq.set`'s `requires 0 <= j < length` is the IndexError obligation; the read
`a[i][j]` is `Seq.get a[i] j`. So a driver proves the mutation reads back:
`(a[i][j] = v; a[i][j]) == v`. The Gate-B spike
(spikes/nested-list-inner-mutable-seq.mlw) proved write-read-back + outer/inner frame
+ dims preservation Valid in BOTH Alt-Ergo and Z3, with the FALSE twin unproven; no
new axiom (Seq/Array laws are Why3 stdlib).

SOUNDNESS (no false claim under aliasing): the value-semantics store diverges from
Python's in-place reference mutation ONLY under inner aliasing, which is UNEXPRESSIBLE
in PyCSL — an inner list can be neither bound to a local (`b = a[i]` type-fails: a
local defaults to int) nor shared across outer slots (`a = [row, row]` type-fails:
`array (array τ)` is rejected). So every expressible post-state is faithful. The
false-twin lock is 0848; a `map`-leaf inner mutation stays fail-closed (0849).
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == v
def str_inner_mutate(a: List[List[str]], i: int, j: int, v: str) -> str:
    a[i][j] = v
    return a[i][j]

if __name__ == "__main__":
    m = [["a", "b", "c"], ["d", "e", "f"]]
    assert str_inner_mutate(m, 1, 2, "Z") == "Z"
    assert m[1][2] == "Z"
