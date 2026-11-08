r"""Test 4253 -- gen #37 route #325 (expected FAIL): `k(F)` into `def k(x: int)` whose contract is `\result == x % 1` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
F = 0.5
#@ ensures \result == x % 1
#@ assigns \nothing
def k(x: int) -> int:
    return x % 1
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    return k(F)

if __name__ == "__main__":
    assert g() == 0, g()
