r"""Test 3981 -- gen #37 route #310 (expected PASS): CONTROL: a tuple with a pure (`assigns \nothing`) user call keeps its erased emission byte-for-byte and proves.
"""
# pycsl-expected: PASS
from typing import List, Tuple, Any, Set, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]
#@ assigns \nothing
#@ ensures \result == a * a
def sq(a: int) -> int:
    return a * a
#@ ensures \result == 0
def f() -> int:
    xs = [0]
    t = (sq(2), 0)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
