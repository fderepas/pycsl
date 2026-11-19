r"""Test 4001 -- gen #37 route #312 census (expected FAIL): `m = max(ys[0:inc(xs)])` -> `max_1 (any int)`, the call vanished.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set

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

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def mks(a: List[int]) -> Set[int]:
    a[0] = a[0] + 1
    return {1}

class K:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {}
        self.s: Set[int] = set()
        self.n: int = 0

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    ys = [1, 2, 3, 4]
    s = "abcd"
    m = max(ys[0:inc(xs)])
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
