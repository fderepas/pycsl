"""1137 — ROUTE #60 NEGATIVE: the CALLER's dict is never consulted.

A dict PARAMETER reaches `_dict_locals` through the mutated-collection-param promotion,
so a single store INVENTED a folded size of 1. `f({5: 5, 6: 6}, 7)` returns 3 in CPython.
Proved before the route #60 whitelist landed; must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 1
#@ assigns d
def f(d: Dict[int, int], k: int) -> int:
    d[k] = 1
    return len(d)
