r"""Test 3983 -- gen #37 route #310 (expected PASS): CONTROL: a tuple-returning function with an effectful element (the value is a real tuple) proves the CPython value.
"""
# pycsl-expected: PASS
from typing import List, Tuple, Any, Set, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]
#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def g(a: List[int]) -> Tuple[int, int]:
    return (inc(a), 0)
#@ ensures \result == 1
def f() -> int:
    xs = [0]
    t = g(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 1
