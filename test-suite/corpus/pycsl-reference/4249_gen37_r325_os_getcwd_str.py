r"""Test 4249 -- gen #37 route #325 (expected FAIL): `c = os.getcwd(); c * 0 == 0` PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import os
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = os.getcwd()
    if c * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
