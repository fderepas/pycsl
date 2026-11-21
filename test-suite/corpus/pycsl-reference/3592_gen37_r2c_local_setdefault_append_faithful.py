r"""Test 3592 — gen #37 r2c-wall R2c-local (expected PASS).

R2c-local: two `by.setdefault("a", []).append(..)` on a local hval dict -> `len(by["a"]) == 2` PROVES (absent key starts from the fresh `[]`).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def w_sd2(n: int) -> int:
    by: Dict[str, PyVal] = {}
    by.setdefault("a", []).append("x")
    by.setdefault("a", []).append("y")
    return len(by["a"])
