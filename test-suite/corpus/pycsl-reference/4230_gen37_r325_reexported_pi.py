r"""Test 4230 -- gen #37 route #325 (expected FAIL): `consts325.PI % 1 == 0` (a user module re-exporting `math.pi`; #322 bypass F1) PROVED through `get_PI` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import multi_file_lib.consts325 as consts325
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if consts325.PI % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
