r"""Test 4009 -- gen #37 route #314 (expected FAIL): `'{a}'.format(a=inc(xs))` -> `format_1 <hash>`, the keyword argument (and its call) dropped; REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    ys = [1, 2, 3, 4]
    s = '{a}'.format(a=inc(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
