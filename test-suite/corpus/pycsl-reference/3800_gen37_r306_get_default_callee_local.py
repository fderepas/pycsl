r"""Test 3800 -- gen #37 route #306 (expected FAIL): a callee `bump(xs)` (contract `assigns a[0]`) passed as the `.get` default of a PRESENT key: Python runs it eagerly (xs[0] becomes 1), so `\result == 0` must not prove (it did: the call sat on the None arm).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == 0
def bump(a: List[int]) -> int:
    a[0] = a[0] + 1
    return 0

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    d: Dict[int, int] = {1: 1}
    y = d.get(1, bump(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
