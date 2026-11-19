r"""Test 7626 -- route #487 control (expected PASS): `if a or b:` over lists (a TRUTH position: the truth value is exact). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
from typing import List

#@ requires len(a) == 2
#@ ensures \result == 1
def f(a: List[int], b: List[int]) -> int:
    if a or b:
        return 1
    return 0
