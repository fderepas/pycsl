r"""Test 4241 -- gen #37 route #325 (expected FAIL): class attribute `C.R = 0.5`: `C.R % 1 == 0` PROVED through `get_R` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    R = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if C.R % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
