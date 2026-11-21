"""1134 — ROUTE #60 NEGATIVE: two stores at the SAME key

`len()` on a dict was a SYNTACTIC count of store sites. This claim is FALSE of the
program and PROVED before the route #60 whitelist landed; it must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {}
    d[1] = 1
    d[1] = 2
    return len(d)
