r"""Test 4336 -- gen #37 route #328 (expected FAIL): `a, b = F, 1` in a function lowers to `let (_tu_a, _tu_b) = (f, 1) in` and the taint was dropped: `a % 1 == 0` PROVED with F = 0.5. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
F = 0.5
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    a, b = F, 1
    return a % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
