r"""Test 4239 -- gen #37 route #325 (expected FAIL): `X = mk()` (a list): `X * 0 == 0` PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
def mk() -> list[int]:
    return [1, 2]
X = mk()
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if X * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
