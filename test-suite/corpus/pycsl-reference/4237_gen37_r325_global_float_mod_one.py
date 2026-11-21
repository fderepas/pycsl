r"""Test 4237 -- gen #37 route #325 (expected FAIL): `F = 0.5; F % 1 == 0` PROVED through `val constant f : int` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
F = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if F % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
