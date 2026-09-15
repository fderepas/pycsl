r"""Test 1376 — ROUTE #131 (parameter arm, order 2): `def f(len, xs): return len(xs)` lowered the call as the builtin array length, so `g() = f(sum, [5])` PROVED `\result == 1` while CPython returns 5. A parameter named like a builtin and read in its function is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ assigns \nothing
def f(len, xs: List[int]) -> int:
    return len(xs)


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    ys: List[int] = [5]
    return f(sum, ys)
