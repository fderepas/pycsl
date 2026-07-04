"""Test 0799 — subscript-projection comprehension is content-faithful.

nested-list.md S4 — LIFTS the cleared-array subscript-projection boundary. Over
`List[List[int]]` (now `array (seq int)`, not the old `array int` collapse), the
comprehension `[x[k] for x in a]` lowers to a per-index `list_content_comp_<n>`
val whose `ensures` gives `length result = length a` and
`forall i. result[i] = Seq.get (a[i]) k` — the SAME inner read a driver's own
`\result[i] == a[i][k]` lowers to. So the column projection proves content-faithful,
which the old opaque `list_comp` (and the collapsed-int element) could not express.
No new axiom (definitional `ensures`; the Seq read law is Why3 stdlib).
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= k
#@ requires \forall i; 0 <= i and i < \length(a) ==> k < len(a[i])
#@ ensures \length(\result) == \length(a)
#@ ensures \forall i; 0 <= i and i < \length(a) ==> \result[i] == a[i][k]
#@ assigns \nothing
def column(a: List[List[int]], k: int) -> List[int]:
    return [x[k] for x in a]

if __name__ == "__main__":
    assert column([[1, 2], [3, 4], [5, 6]], 1) == [2, 4, 6]
