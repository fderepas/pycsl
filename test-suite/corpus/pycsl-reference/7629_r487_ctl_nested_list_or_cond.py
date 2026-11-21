r"""Test 7629 -- route #487 control (expected PASS): `if (a or b) and n == n:` (a nested BoolOp in a truth position). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
from typing import List

#@ requires len(a) == 1
#@ ensures \result == 1
def f(a: List[int], b: List[int], n: int) -> int:
    if (a or b) and n == n:
        return 1
    return 0
