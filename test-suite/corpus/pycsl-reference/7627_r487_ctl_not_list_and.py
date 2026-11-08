r"""Test 7627 -- route #487 control (expected PASS): `if not (a and b):` over lists (a truth position). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
from typing import List

#@ requires len(a) == 0
#@ ensures \result == 1
def f(a: List[int], b: List[int]) -> int:
    if not (a and b):
        return 1
    return 0
