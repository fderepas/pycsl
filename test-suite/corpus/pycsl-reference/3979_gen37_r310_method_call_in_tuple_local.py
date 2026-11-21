r"""Test 3979 -- gen #37 route #310 (expected FAIL): `t = (k.bump(), 0)`: the erased tuple binding dropped the method call's field write; now evaluated.
"""
# pycsl-expected: FAIL
from typing import List, Tuple, Any, Set, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class K:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1 and \result == self.n
    def bump(self) -> int:
        self.n = self.n + 1
        return self.n

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = K()
    t = (k.bump(), 0)
    return k.n

if __name__ == "__main__":
    assert f() == 0
