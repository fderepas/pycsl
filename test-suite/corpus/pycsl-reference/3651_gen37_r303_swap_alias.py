r"""Test 3651 -- gen #37 route #303 (expected FAIL): REFUSAL: `g, h = h, h; h["G"] = 5; return g["G"]` (a non-permutation swap aliases g and h) PROVED 0; CPython 5. Refused at emit (PYCSL-M6-MUTATION-THROUGH-UNPACK-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    g, h = h, h
    h["G"] = 5
    return g["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
