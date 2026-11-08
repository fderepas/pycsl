r"""Test 1361 — ROUTE #129: `setn()` writes `N` through `global`; the store lowered to a FRESH local while both reads of the non-constant module variable `N` were one opaque constant, so `a = N; setn(); return a - N` PROVED `\result == 0` while CPython returns -2 (under a false `assigns \nothing`; the honest `assigns N` is not expressible). A `global` write to a non-`#@ shared` name is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

XS: List[int] = [1, 2, 3]
N = len(XS)


#@ assigns \nothing
def setn() -> None:
    global N
    N = 5


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = N
    setn()
    return a - N
