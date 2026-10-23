"""1143 — ROUTE #61 NEGATIVE: a dict literal with NON-CONSTANT keys.

`requires a == b` hands the prover the key collision as a FACT, and the size fold answered
2 anyway because it counted syntactic entries and never consulted the map. CPython answers
1. PROVED before the route #61 repair; must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Dict


#@ requires a == b
#@ ensures \result == 2
#@ assigns \nothing
def f(a: int, b: int) -> int:
    d: Dict[int, int] = {a: 1, b: 2}
    return len(d)
