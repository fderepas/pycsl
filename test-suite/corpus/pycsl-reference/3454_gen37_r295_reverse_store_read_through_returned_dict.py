r"""Test 3454 -- route #295 (expected FAIL): REVERSE: `e = idd(d); d[1] = 2; return e[1]` with a verified `ensures \result == x` identity PROVED `\result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List

#@ ensures \result == x
#@ assigns \nothing
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ ensures \result == 1
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    e = idd(d)
    d[1] = 2
    return e[1]

if __name__ == "__main__":
    assert f(1) == 2, f(1)
