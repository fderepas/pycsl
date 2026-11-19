r"""Test 3461 -- route #295 (expected FAIL): a NEW key `e[5] = 5` through the returned alias PROVED `5 not in d`; CPython: it is in. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List

#@ assigns \nothing
#@ \trusted
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ ensures \result == 0
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    e = idd(d)
    e[5] = 5
    return 1 if 5 in d else 0

if __name__ == "__main__":
    assert f(1) == 1, f(1)
