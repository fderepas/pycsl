r"""Test 4255 -- gen #37 route #325 (expected FAIL): `y = F if c else 0; y % 1 == 0` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
F = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g(c: bool) -> int:
    y = F if c else 0
    if y % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g(True) == 1
