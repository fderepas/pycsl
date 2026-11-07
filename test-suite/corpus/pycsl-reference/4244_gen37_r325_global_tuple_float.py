r"""Test 4244 -- gen #37 route #325 (expected FAIL): `T = (0.5, 1); T[0] % 1 == 0` PROVED through `subscript_get` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
T = (0.5, 1)
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if T[0] % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
