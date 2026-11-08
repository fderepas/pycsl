r"""Test 3662 -- gen #37 route #303 (expected FAIL): REFUSAL: the chained `h = k = g` of a declared dict `h` (desugared to rebinds) then `h["G"] = 5; return g["G"]` PROVED 0; CPython 5. Refused by the #59 guard.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    h = k = g
    h["G"] = 5
    return g["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
