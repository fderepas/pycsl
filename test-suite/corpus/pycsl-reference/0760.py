"""Test 0760 — `sorted(a)` is content-faithful: sorted AND a permutation.

cleared-array.md S5 (spike S0-bis proven Valid on Alt-Ergo + Z3). The abstract
`sorted_1` val now carries three DEFINITIONAL `ensures` (length, adjacent
sortedness, `permut result a`) discharged at the USE site — NO global axiom.
A driver can therefore prove that the result of `sorted` is both sorted
(`\is_sorted`) and a permutation of the input (`\permutation`), which the old
opaque `sorted_1` could not establish.
"""
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(\result) - 1 ==> \result[k] <= \result[k + 1]
#@ ensures \permutation(\result, a)
#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def sort_it(a: List[int]) -> List[int]:
    return sorted(a)
