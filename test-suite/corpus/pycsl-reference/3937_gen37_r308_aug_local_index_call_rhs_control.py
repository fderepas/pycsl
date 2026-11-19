r"""Test 3937 -- gen #37 route #308 (expected PASS): CONTROL: a local index with an effectful right-hand side keeps today's lowering and proves.
"""
# pycsl-expected: PASS
from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 1
def f() -> int:
    c = [0]
    ys = [0, 0, 0]
    i = 2
    ys[i] += inc(c)
    return ys[2]

if __name__ == "__main__":
    assert f() == 1
