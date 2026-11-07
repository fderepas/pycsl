r"""Test 4335 -- gen #37 route #328 (expected FAIL): module-level `A, *REST = [0.5, 1]`: `A % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
A, *REST = [0.5, 1]
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A * 2 == 2 * A and A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
