r"""Test 3458 -- route #295 (expected FAIL): `e: Dict[int, int] = d if c > 0 else {1: 5}; e[1] = 2` PROVED `c > 0 ==> \result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List

#@ ensures c > 0 ==> \result == 1
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    e: Dict[int, int] = d if c > 0 else {1: 5}
    e[1] = 2
    return d[1]

if __name__ == "__main__":
    assert f(1) == 2, f(1)
