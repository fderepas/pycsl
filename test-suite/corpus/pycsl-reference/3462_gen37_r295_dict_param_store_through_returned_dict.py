r"""Test 3462 -- route #295 (expected FAIL): on a dict PARAMETER under `assigns d`: `e = idd(d); e[1] = e[1] + 1; return d[1]` PROVED `\result == \old(d[1])`; CPython: old + 1. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict

#@ assigns \nothing
#@ \trusted
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ requires 1 in d
#@ ensures \result == \old(d[1])
#@ assigns d
def f(d: Dict[int, int]) -> int:
    e = idd(d)
    e[1] = e[1] + 1
    return d[1]

if __name__ == "__main__":
    dd = {1: 1}
    r = f(dd)
    assert r == 2, r
