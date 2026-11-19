r"""Test 4248 -- gen #37 route #325 (expected FAIL): `r = random.random(); r * 2 // 2 == r` PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import random
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    r = random.random()
    if r * 2 // 2 == r:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
