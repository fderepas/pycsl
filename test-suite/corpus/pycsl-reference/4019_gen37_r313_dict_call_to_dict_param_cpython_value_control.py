r"""Test 4019 -- gen #37 route #313 (expected PASS): CONTROL: `gd(mkd(xs))` then `xs[0] == 1` (CPython value).
"""
# pycsl-expected: PASS
from typing import List, Dict, Set

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

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def mkl(a: List[int]) -> List[int]:
    a[0] = a[0] + 1
    return [1]

#@ ensures \result == 0
def gd(p: Dict[int, int]) -> int:
    return 0

#@ ensures \result == 0
def gs(p: Set[int]) -> int:
    return 0

#@ ensures \result == 0
def gl(p: List[int]) -> int:
    return 0

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    v = gd(mkd(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 1, f()
