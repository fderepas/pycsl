r"""Test 2546 — route #254 (expected FAIL): one dict passed to the MUTATING slot `x` (`del x[1]`) and the
read slot `y` of `g` (`requires 1 in y`, returns `1 in y`): `return g(a, a)` PROVED `\result == True`.
CPython: `m()` is False (the key was deleted through `x`). PROVED at e6f26cde; now REFUSED fail-closed
(PYCSL-WHYML-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ requires 1 in y
#@ ensures \result == True
#@ assigns x
def g(x: Dict[int, int], y: Dict[int, int]) -> bool:
    if 1 in x:
        del x[1]
    return 1 in y


#@ ensures \result == True
#@ assigns \nothing
def m() -> bool:
    a: Dict[int, int] = {1: 2}
    return g(a, a)


if __name__ == "__main__":
    print(m())
