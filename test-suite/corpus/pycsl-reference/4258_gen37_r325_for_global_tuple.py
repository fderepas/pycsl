r"""Test 4258 -- gen #37 route #325 (expected FAIL): `for v in T` over a global float tuple, `v % 1 != 0` never taken (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
T = (0.5, 1.5)
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    for v in T:
        if v % 1 != 0:
            return 0
    return 1

if __name__ == "__main__":
    assert g() == 1, g()
