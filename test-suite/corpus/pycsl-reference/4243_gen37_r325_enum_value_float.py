r"""Test 4243 -- gen #37 route #325 (expected FAIL): `Color.RED.value` (0.5) `% 1 == 0` PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from enum import Enum
class Color(Enum):
    RED = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if Color.RED.value % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
