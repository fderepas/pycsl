r"""Test 2542 — route #254 (expected FAIL): the same set passed positionally to the MUTATING slot and by
KEYWORD to the read slot: `return g(a, y=a)` PROVED `\result == False`.
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
    return g(a, y=a)


if __name__ == "__main__":
    print(m())
