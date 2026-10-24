r"""Test 4246 -- gen #37 route #325 (expected FAIL): user-module attribute `consts325.S = "ab"`: `S * 0 == 0` PROVED (CPython `"" == 0` is False) (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import multi_file_lib.consts325 as consts325
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if consts325.S * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
