r"""Test 4300 -- gen #37 route #327 (expected FAIL): `N = len(xs); n = 0; return N == n`: `N` and `n` fold to one WhyML `n` and `!n = !n` PROVED True (CPython False). REFUSED (PYCSL-R327-IDENT-COLLISION).
"""
# pycsl-expected: FAIL
from typing import List
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List[int]) -> bool:
    N = len(xs)
    n = 0
    return N == n

if __name__ == "__main__":
    assert g([1, 2]) == True
