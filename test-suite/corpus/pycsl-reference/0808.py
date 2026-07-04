"""Test 0808 — target-DEPENDENT comprehension index is content-faithful.

nested-list.md §8/§9 EXTENSION (target-dependent index). The subscript-projection
comprehension `[x[len(x)-1] for x in a]` over `List[List[int]]` (~ `array (seq int)`)
uses an index that DEPENDS on the loop target `x` (the last element of each row).
It lowers to a per-index `list_content_comp_<n>` val whose `ensures` gives
    forall i. result[i] = Seq.get (a[i]) (Seq.length (a[i]) - 1)
— the SAME inner read a driver's own `\result[i] == a[i][len(a[i])-1]` lowers to
(the index `len(x)-1` lifts to a pure int term over `Seq.length` of the per-index
row). So the target-dependent column projection proves content-faithful. No new
axiom (definitional `ensures`; Seq read/length laws are Why3 stdlib).
"""
_ = 0  # anchor
from typing import List

#@ requires \forall i; 0 <= i and i < \length(a) ==> len(a[i]) >= 1
#@ ensures \length(\result) == \length(a)
#@ ensures \forall i; 0 <= i and i < \length(a) ==> \result[i] == a[i][len(a[i]) - 1]
#@ assigns \nothing
def last_col(a: List[List[int]]) -> List[int]:
    return [x[len(x) - 1] for x in a]

if __name__ == "__main__":
    assert last_col([[1, 2], [3, 4, 5], [6]]) == [2, 5, 6]
