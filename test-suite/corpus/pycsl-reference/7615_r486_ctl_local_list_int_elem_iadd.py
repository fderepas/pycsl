r"""Test 7615 -- route #486 control (expected PASS): `c = [0, 0]; c[0] += 1` (a local list of ints). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
from typing import List

#@ ensures \result == 1
def f() -> int:
    c = [0, 0]
    c[0] += 1
    return c[0]
