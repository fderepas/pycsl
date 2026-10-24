r"""Test 4261 -- gen #37 route #325 (expected FAIL): `def r(self) -> int: return self.R` (R = 0.5) then `c.r() % 1 == 0` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    R = 0.5
    #@ assigns \nothing
    def r(self) -> int:
        return self.R
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    if c.r() % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
