r"""Test 3650 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = g, 1; h["G"] = 5; return g["G"]` -- the unpacking lowered to a COPY of `g`, so `\result == 0` PROVED; CPython 5. Refused at emit (PYCSL-M6-MUTATION-THROUGH-UNPACK-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    h, k = g, 1
    h["G"] = 5
    return g["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
