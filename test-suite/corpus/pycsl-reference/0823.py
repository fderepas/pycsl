"""Test 0823 — WL-05 regression guard (POSITIVE, set twin of 0822): LOCAL set add-membership proves.

wrong-lowering-to-fix.md §WL-05. The complement of the 0821 rejection: a mutation of
a LOCAL set (a `ref`, with a genuine mutation frame) is faithfully modelled and PROVES.
After `s.add(5)`, the membership `5 in s` holds. This guards the WL-05 fix from
over-rejecting: only dict/set PARAMETER mutation is out of scope; LOCAL collection
mutation is fully supported. If this ever FAILS, the fix has over-reached and broken
the faithful local-set model.
"""
_ = 0  # anchor
from typing import Set


#@ ensures \result == 1
def local_set_add_membership() -> int:
    s: Set[int] = set()
    s.add(5)
    if 5 in s:
        return 1
    return 0
