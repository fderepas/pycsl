r"""Test 4231 -- gen #37 route #325 (expected FAIL): `from <user module> import PI; PI % 1 == 0` (#322 bypass F1) PROVED through `val constant pI : int` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from multi_file_lib.consts325 import PI
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if PI % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
