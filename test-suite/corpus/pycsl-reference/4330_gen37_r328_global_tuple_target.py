r"""Test 4330 -- gen #37 route #328 (expected FAIL): `A, B = 0.5, 1` at module level: `A % 1 == 0` PROVED (the origin census read only simple `Name = ..`; CPython violates). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
A, B = 0.5, 1
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
