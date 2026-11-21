r"""Test 3655 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = p, 1; h["G"] = 5; return p["G"]` (p a dict parameter; FAIL at base, now refused at emit).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(p: Dict[str, int]) -> int:
    h: Dict[str, int] = {"G": 0}
    h, k = p, 1
    h["G"] = 5
    return p["G"]

if __name__ == "__main__":
    assert f({"G": 0}) == 0, f({"G": 0})
