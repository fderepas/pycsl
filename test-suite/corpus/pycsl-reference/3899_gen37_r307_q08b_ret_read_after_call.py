r"""Test 3899 -- gen #37 route #307 (expected FAIL): `xs[0] + inc(xs) * 2` read the element after the call wrote it; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe q08b_ret_read_after_call).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 3
def f() -> int:
    xs = [0]
    return xs[0] + inc(xs) * 2

if __name__ == "__main__":
    assert f() == 3
