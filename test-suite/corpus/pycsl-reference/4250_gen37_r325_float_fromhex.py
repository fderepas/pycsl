r"""Test 4250 -- gen #37 route #325 (expected FAIL): `float.fromhex("0x1.8p0") % 1 == 0` PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = float.fromhex("0x1.8p0")
    if x % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
