r"""Test 3817 -- gen #37 route #306 (expected PASS): CONTROL (coverage): PRESENT key, the callee default STILL runs: `xs[0] == 1` proves (it failed before #306).
"""
# pycsl-expected: PASS
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == 0
def bump(a: List[int]) -> int:
    a[0] = a[0] + 1
    return 0

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    d: Dict[int, int] = {1: 1}
    y = d.get(1, bump(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 1
