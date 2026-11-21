r"""Test 4332 -- gen #37 route #328 (expected FAIL): `if True: A = 0.5` at module level: `A % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
if True:
    A = 0.5
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
