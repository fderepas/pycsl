r"""Test 1700 - ROUTE #201 control (gen #30): the repair touches only the UNRECOVERABLE tail. A genuine list actual still reaches the callee with the length it has, and the callee's length-reading contract still discharges in the caller. Without this control the #201 fix could have been the blunt one - making every array-slot actual opaque - and the corpus would not have noticed.
"""
# pycsl-expected: PASS
from typing import List

_ = 0  # anchor


#@ requires True
#@ ensures len(p) == 3 ==> \result == 1
#@ ensures len(p) != 3 ==> \result == 2
def callee(p: List[int]) -> int:
    if len(p) == 3:
        return 1
    return 2


#@ ensures \result == 1
def probe() -> int:
    return callee([7, 8, 9])
