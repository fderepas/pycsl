"""Test 0761 — identity list comprehension is content-faithful.

cleared-array.md S1. `[x for x in a]` now lowers to a per-instance
`list_content_comp_<n>` val whose `ensures` gives `length result = length a`
and `forall i. result[i] = a[i]` — so a driver can prove the result is an
element-wise copy of the source, which the old opaque `list_comp` (a bare int
`0`) could not express at all.
"""
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == a[k]
#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def copy_list(a: List[int]) -> List[int]:
    return [x for x in a]
