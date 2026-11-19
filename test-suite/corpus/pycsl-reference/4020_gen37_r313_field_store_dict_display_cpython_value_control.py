r"""Test 4020 -- gen #37 route #313 (expected PASS): CONTROL: `k.d = {0: inc(xs)}` then `xs[0] == 1` (CPython value).
"""
# pycsl-expected: PASS
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

class K:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {}
        self.s: Set[int] = set()

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    k = K()
    e: Dict[int, int] = {5: 5}
    k.d = {0: inc(xs)}
    return xs[0]

if __name__ == "__main__":
    assert f() == 1, f()
