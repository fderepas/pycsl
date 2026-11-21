r"""Test 2545 — route #254 (expected FAIL): the duplicate one call AWAY: `mm(p, q)` forwards `p` into
`g`'s mutating slot (so `p` mutates too) and `q` into its read slot; `return mm(a, a)` PROVED `\result == False`.
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


#@ requires not (1 in q)
#@ ensures \result == False
#@ assigns p
def mm(p: Set[int], q: Set[int]) -> bool:
    return g(p, q)


#@ ensures \result == False
#@ assigns \nothing
def m() -> bool:
    a: Set[int] = set()
    return mm(a, a)


if __name__ == "__main__":
    print(m())
