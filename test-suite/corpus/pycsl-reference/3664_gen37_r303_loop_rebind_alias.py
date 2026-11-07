r"""Test 3664 -- gen #37 route #303 (expected FAIL): REFUSAL: a dict REBIND `h = g` at the END of a loop body whose store `h["G"] = 5` sits at the TOP (the next iteration writes `g`) -- route #59 walked only the statements after the binding; `\result == 0` PROVED, CPython 5. Refused by the #59 guard.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 0}
    i = 0
    #@ loop invariant 0 <= i <= 2
    #@ loop variant 2 - i
    while i < 2:
        h["G"] = 5
        h = g
        i = i + 1
    return g["G"]

if __name__ == "__main__":
    assert f(0) == 0, f(0)
