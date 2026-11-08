r"""Test 4257 -- gen #37 route #325 (expected FAIL): `x = float(s); x < 5 or x >= 5` (s = "nan": CPython False) (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def g(s: str) -> int:
    x = float(s)
    if x < 5 or x >= 5:
        return 1
    return 0

if __name__ == "__main__":
    assert g("nan") == 1, g("nan")
