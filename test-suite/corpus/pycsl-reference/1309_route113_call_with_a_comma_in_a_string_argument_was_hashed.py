r"""Test 1309 — ROUTE #113 negative: `[g(y, "a,b")]` was classified a TUPLE by the comma inside the string literal and the whole call replaced by a hash of its TEXT, so `b - a == 0` PROVED over g(y) before and after y += 1 (CPython 1). The call now passes through; the claim is refused. Faithful twin: 1310.
"""
# pycsl-expected: FAIL
from typing import List

#@ ensures \result == x
#@ assigns \nothing
def g(x: int, s: str) -> int:
    return x

#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    xs: List[int] = [g(y, "a,b")]
    a = xs[0]
    y = y + 1
    ys: List[int] = [g(y, "a,b")]
    b = ys[0]
    return b - a
