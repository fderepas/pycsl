r"""Test 3943 -- gen #37 route #309 (expected FAIL): `getattr(k, "zz", inc(xs))` on an absent attribute: the default's write vanished; now the default itself is the answer.
"""
# pycsl-expected: FAIL
from typing import List

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
    y = getattr(k, "zz", inc(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
