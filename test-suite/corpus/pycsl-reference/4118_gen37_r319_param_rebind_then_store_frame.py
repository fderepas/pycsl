r"""Test 4118 -- gen #37 route #319 (expected FAIL): `if b: xs = [7, 7]; xs[0] = 5` then `xs[0] = 9` wrote the CALLER list after the block; `ensures xs[0] == 9` under `assigns xs[0]` PROVED (CPython: caller untouched). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List
#@ requires len(xs) == 2 and xs[0] == 1
#@ assigns xs[0]
#@ ensures xs[0] == 9
def f(xs: List[int], b: bool) -> None:
    if b:
        xs = [7, 7]
        xs[0] = 5
    xs[0] = 9

if __name__ == "__main__":
    a = [1, 2]
    f(a, True)
    assert a[0] == 9, a
