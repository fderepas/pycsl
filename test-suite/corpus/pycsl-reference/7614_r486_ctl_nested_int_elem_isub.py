r"""Test 7614 -- route #486 control (expected PASS): `a[0][0] -= 1` on `a: List[List[int]]` (an int element, rt40 w9715). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
from typing import List

#@ requires len(a) == 1 and len(a[0]) == 1
#@ no_exception \all
def f(a: List[List[int]]) -> int:
    a[0][0] -= 1
    return 0
