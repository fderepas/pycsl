"""1139 — ROUTE #60 NEGATIVE: a store in a LOOP body was counted ONCE.

Building a dict in a loop and asking its size is one of the commonest idioms in Python.
CPython answers `n`; the claim below was proved for EVERY n > 0. The most damaging
carrier of the route.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Dict


#@ requires n > 0
#@ ensures \result == 1
#@ assigns \nothing
def f(n: int) -> int:
    d: Dict[int, int] = {}
    #@ loop invariant 0 <= i <= n
    #@ loop variant n - i
    for i in range(n):
        d[i] = i
    return len(d)
