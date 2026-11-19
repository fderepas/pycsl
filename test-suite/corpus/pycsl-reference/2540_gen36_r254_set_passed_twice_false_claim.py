r"""Test 2540 — route #254 (expected FAIL): one set passed to the MUTATING slot `x` and the read slot `y` of
`g` (`x.add(1); return 1 in y` under `requires not (1 in y)`): `return g(a, a)` PROVED `\result == False`.
CPython: `m()` is True (one object, mutated through `x`, read through `y`). PROVED at e6f26cde; now
REFUSED fail-closed (PYCSL-WHYML-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Set


#@ requires not (1 in y)
#@ ensures \result == False
#@ assigns x
def g(x: Set[int], y: Set[int]) -> bool:
    x.add(1)
    return 1 in y


#@ ensures \result == False
#@ assigns \nothing
def m() -> bool:
    a: Set[int] = set()
    return g(a, a)


if __name__ == "__main__":
    print(m())
