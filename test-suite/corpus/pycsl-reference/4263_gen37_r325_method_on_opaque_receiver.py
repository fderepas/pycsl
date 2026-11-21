r"""Test 4263 -- gen #37 route #325 (expected FAIL): `c = os.getcwd(); c.upper() * 0 == 0` (receiver dropped by the stub `c_upper_0`) (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import os
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = os.getcwd()
    if len(c.upper()) * 0 == 0 and c.upper() * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
