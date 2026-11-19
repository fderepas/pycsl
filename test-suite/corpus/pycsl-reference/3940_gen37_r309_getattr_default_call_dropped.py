r"""Test 3940 -- gen #37 route #309 (expected FAIL): `getattr(k, "n", inc(xs))`: the call default lowered to a shared constant and inc's write vanished; the default is now evaluated before the field read.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class K:
    def __init__(self) -> None:
        self.n = 4

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = K()
    y = getattr(k, "n", inc(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
