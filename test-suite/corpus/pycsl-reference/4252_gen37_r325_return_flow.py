r"""Test 4252 -- gen #37 route #325 (expected FAIL): `def h() -> float: return F` then `h() % 1 == 0` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
F = 0.5
def h() -> float:
    return F
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if h() % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
