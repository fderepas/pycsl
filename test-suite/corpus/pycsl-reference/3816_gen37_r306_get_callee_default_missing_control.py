r"""Test 3816 -- gen #37 route #306 (expected PASS): CONTROL: missing key, callee default runs: `xs[0] == 1` proves.
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
    y = d.get(2, bump(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 1
