r"""Test 3659 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = idt(g)` where `idt` returns `(d, 1)`, then `h["G"] = 5` (L3-tc FAIL at base, now refused at emit).
"""
# pycsl-expected: FAIL
from typing import Dict, Tuple


#@ assigns \nothing
def idt(d: Dict[str, int]) -> Tuple[Dict[str, int], int]:
    return d, 1


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    h, k = idt(g)
    h["G"] = 5
    return g["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
