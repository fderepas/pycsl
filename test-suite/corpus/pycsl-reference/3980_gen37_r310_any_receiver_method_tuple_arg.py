r"""Test 3980 -- gen #37 route #310 (expected FAIL): `o.m((inc(xs), 0))` on an `Any` receiver: the display argument was coerced to `(any int)`; now evaluated first.
"""
# pycsl-expected: FAIL
from typing import List, Tuple, Any, Set, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]
class O:
    def m(self, v: Any) -> int:
        return 0
    def __getitem__(self, k: Any) -> int:
        return 0
    def __add__(self, k: Any) -> int:
        return 0

#@ ensures \result == 0
def f(o: Any) -> int:
    xs = [0]
    o.m((inc(xs), 0))
    return xs[0]

if __name__ == "__main__":
    assert f(O()) == 0
