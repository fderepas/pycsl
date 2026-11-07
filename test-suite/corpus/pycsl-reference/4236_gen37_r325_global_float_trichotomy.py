r"""Test 4236 -- gen #37 route #325 (expected FAIL): `EPS = 0.5`: `x < EPS or x >= EPS + 1 or x == EPS` PROVED (false at x = 1) (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
EPS = 0.5
#@ requires x >= 0
#@ ensures \result == True
#@ assigns \nothing
def g(x: int) -> bool:
    return x < EPS or x >= EPS + 1 or x == EPS

if __name__ == "__main__":
    assert g(1) == True, g(1)
