r"""Test 1533 - ROUTE #157 control (gen #29): an EQUAL-length slice assignment `a[0:2] = [7, 8]` discharges the new length obligation and `a[1] == 8` PROVES on both sides of the repair.
"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 8
def probe() -> int:
    a: List[int] = [1, 2]
    a[0:2] = [7, 8]
    return a[1]

