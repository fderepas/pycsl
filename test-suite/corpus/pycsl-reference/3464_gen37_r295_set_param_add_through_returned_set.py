r"""Test 3464 -- route #295 (expected FAIL): a `Set[int]` PARAMETER: `t = ids(s); t.add(5); return 5 in s` PROVED `\result == 0`; CPython: 1. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Set

#@ assigns \nothing
#@ \trusted
def ids(x: Set[int]) -> Set[int]:
    return x

#@ requires not (5 in s)
#@ ensures \result == 0
#@ assigns s
def f(s: Set[int]) -> int:
    t = ids(s)
    t.add(5)
    return 1 if 5 in s else 0

if __name__ == "__main__":
    assert f(set()) == 1
