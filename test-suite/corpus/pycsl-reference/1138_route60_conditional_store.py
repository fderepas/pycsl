"""1138 — ROUTE #60 NEGATIVE: a store the run may never execute is still counted.

`f(0)` returns 1 in CPython. The claim below was proved for EVERY `c`. This carrier is
about REACHABILITY, not key equality — every key here is distinct.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    if c > 0:
        d[2] = 2
    return len(d)
