r"""Test 3459 -- route #295 (expected FAIL): `e = idd(idd(d)); e[1] = 2` PROVED `\result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List

#@ assigns \nothing
#@ \trusted
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ ensures \result == 1
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    e = idd(idd(d))
    e[1] = 2
    return d[1]

if __name__ == "__main__":
    assert f(1) == 2, f(1)
