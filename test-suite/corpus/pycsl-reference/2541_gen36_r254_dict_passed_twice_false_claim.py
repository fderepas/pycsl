r"""Test 2541 — route #254 (expected FAIL): one dict passed to the MUTATING slot `x` (`x[1] = 5`) and the read
slot `y` of `g`: `return g(a, a)` PROVED `\result == False`.
CPython: `m()` is True (one object, mutated through `x`, read through `y`). PROVED at e6f26cde; now
REFUSED fail-closed (PYCSL-WHYML-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict


#@ requires not (1 in y)
#@ ensures \result == False
#@ assigns x
def g(x: Dict[int, int], y: Dict[int, int]) -> bool:
    x[1] = 5
    return 1 in y


#@ ensures \result == False
#@ assigns \nothing
def m() -> bool:
    a: Dict[int, int] = {}
    return g(a, a)


if __name__ == "__main__":
    print(m())
