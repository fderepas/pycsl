r"""Test 3653 -- gen #37 route #303 (expected FAIL): REFUSAL: the r2c-local path write-back through `h, k = p, 1` (p a PARAMETER) PROVED under `assigns \nothing` while the caller's dict is mutated. Refused at emit.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(p: Dict[str, PyVal]) -> int:
    h: Dict[str, PyVal] = {"G": {"m": []}}
    h, k = p, 1
    h["G"]["m"].append("x")
    return 0

if __name__ == "__main__":
    p: Dict[str, PyVal] = {"G": {"m": []}}
    assert f(p) == 0
    assert len(p["G"]["m"]) == 0, p
