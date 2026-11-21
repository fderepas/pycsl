r"""Test 3593 — gen #37 r2c-wall R2c-local (expected FAIL).

False twin of 3592: `== 1` (CPython: 2) must NOT prove.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def w_sd2_twin(n: int) -> int:
    by: Dict[str, PyVal] = {}
    by.setdefault("a", []).append("x")
    by.setdefault("a", []).append("y")
    return len(by["a"])
