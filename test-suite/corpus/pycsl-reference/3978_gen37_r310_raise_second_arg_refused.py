r"""Test 3978 -- gen #37 route #310 (expected FAIL): `raise ValueError("m", inc(xs))`: Module 5 keeps only the first argument, so the second's call vanished; REFUSED (route #310, `PYCSL-SEM-ERASED-EFFECT-R310`).
"""
# pycsl-expected: FAIL
from typing import List, Tuple, Any, Set, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    try:
        raise ValueError("m", inc(xs))
    except ValueError:
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
