"""1133 — ROUTE #60 NEGATIVE: a store at a key the LITERAL already has

`len()` on a dict was a SYNTACTIC count of store sites. This claim is FALSE of the
program and PROVED before the route #60 whitelist landed; it must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Dict

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    d[1] = 2
    return len(d)
