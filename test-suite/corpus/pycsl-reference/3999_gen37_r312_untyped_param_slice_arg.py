r"""Test 3999 -- gen #37 route #312 (expected FAIL): `g(ys[0:inc(xs)])` with an unannotated parameter -> `g (any int)`, the call vanished.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Any

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def mkd(a: List[int]) -> Dict[int, int]:
    a[0] = a[0] + 1
    return {0: 1}

#@ ensures \result == 0
def g(p) -> int:
    return 0

#@ ensures \result == 0
def gd(p: Dict[int, int]) -> int:
    return 0

class K:
    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == 0
    def m(self, p) -> int:
        return 0

    #@ ensures \result == 0
    def md(self, p: Dict[int, int]) -> int:
        return 0

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    ys = [1, 2, 3, 4]
    k = K()
    v = g(ys[0:inc(xs)])
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
