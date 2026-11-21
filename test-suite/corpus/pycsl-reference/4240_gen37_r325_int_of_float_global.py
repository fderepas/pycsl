r"""Test 4240 -- gen #37 route #325 (expected FAIL): `F = 2.5; int(F) == F` PROVED (lowered to `f = f`) (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
F = 2.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if int(F) == F:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
