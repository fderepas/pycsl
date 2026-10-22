r"""Test 3661 -- gen #37 route #303 (expected FAIL): REFUSAL: a REBIND `h = g` of an already-declared dict local lowered to `h := !g` (a COPY) and was outside route #59's first-binding guard: `h["G"] = 5; return g["G"]` PROVED 0; CPython 5. Refused by the #59 guard (PYCSL #59 message).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    h = g
    h["G"] = 5
    return g["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
