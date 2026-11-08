r"""Test 4245 -- gen #37 route #325 (expected FAIL): user-module attribute `consts325.F = 0.5`: `% 1 == 0` PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import multi_file_lib.consts325 as consts325
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if consts325.F % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
