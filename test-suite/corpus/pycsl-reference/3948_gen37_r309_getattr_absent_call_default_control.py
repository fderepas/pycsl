r"""Test 3948 -- gen #37 route #309 (expected PASS): CONTROL: an absent attribute answers the evaluated default (`y == xs[0]` proves).
"""
# pycsl-expected: PASS
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
    return y - xs[0]

if __name__ == "__main__":
    assert f() == 0
