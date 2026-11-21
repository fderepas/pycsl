r"""Test 2543 — route #254 (expected FAIL): a second LOCAL name for the set (`b = a`) in the read slot:
`return g(a, b)` PROVED `\result == False`.
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
    b = a
    return g(a, b)


if __name__ == "__main__":
    print(m())
