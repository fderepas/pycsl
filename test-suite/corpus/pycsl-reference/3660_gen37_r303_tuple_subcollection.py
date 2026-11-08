r"""Test 3660 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = g["G"], 1; h["m"].append("x")` (a sub-collection read aliases g's inner dict; L3-tc FAIL at base, now refused at emit).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, PyVal] = {"G": {"m": []}}
    h: Dict[str, PyVal] = {"m": []}
    h, k = g["G"], 1
    h["m"].append("x")
    return len(g["G"]["m"])

if __name__ == "__main__":
    assert f(0) == 0, f(0)
