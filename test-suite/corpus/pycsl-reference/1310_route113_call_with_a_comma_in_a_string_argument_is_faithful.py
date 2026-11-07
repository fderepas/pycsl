r"""Test 1310 — ROUTE #113 faithful twin: with the call kept, the TRUE `b - a == 1` PROVES (it was refused while the call was a constant hash). Negative: 1309.
"""
from typing import List

#@ ensures \result == x
#@ assigns \nothing
def g(x: int, s: str) -> int:
    return x

#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    xs: List[int] = [g(y, "a,b")]
    a = xs[0]
    y = y + 1
    ys: List[int] = [g(y, "a,b")]
    b = ys[0]
    return b - a
