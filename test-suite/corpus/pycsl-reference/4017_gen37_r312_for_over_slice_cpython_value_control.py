r"""Test 4017 -- gen #37 route #312 (expected PASS): CONTROL: `for v in ys[0:inc(xs)]` then `xs[0] == 1` (CPython value).
"""
# pycsl-expected: PASS
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    ys = [1, 2, 3, 4]
    for v in ys[0:inc(xs)]:
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 1, f()
