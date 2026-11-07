"""1136 — ROUTE #60 NEGATIVE: a SYMBOLIC store key.

Whether the length grows is undecidable at emission (`k` may be 1), so any constant is
wrong on some input. Proved before the route #60 whitelist landed; must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f(k: int) -> int:
    d: Dict[int, int] = {1: 1}
    d[k] = 2
    return len(d)
