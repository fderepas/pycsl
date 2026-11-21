r"""Test 4334 -- gen #37 route #328 (expected FAIL): module-level walrus `(A:= 0.5)`: `A % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
if (A := 0.5):
    pass
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
