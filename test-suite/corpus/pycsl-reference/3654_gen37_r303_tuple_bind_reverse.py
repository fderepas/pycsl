r"""Test 3654 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = g, 1; g["G"] = 5; return h["G"]` (store through the SOURCE) PROVED 0; CPython 5. Refused at emit.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    h, k = g, 1
    g["G"] = 5
    return h["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
