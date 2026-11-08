r"""Test 3810 -- gen #37 route #306 (expected FAIL): Python evaluates the KEY before the DEFAULT: `d.get(bump(xs), bump(xs))` looks up 1 (-> 7), not 2 (-> 9); claiming 9 must not prove.
"""
# pycsl-expected: FAIL
from typing import Dict, List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def bump(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ requires len(xs) == 1 and xs[0] == 0
#@ assigns xs[0]
#@ ensures \result == 9
def f(xs: List[int]) -> int:
    d: Dict[int, int] = {1: 7, 2: 9}
    return d.get(bump(xs), bump(xs))

if __name__ == "__main__":
    assert f([0]) == 9
