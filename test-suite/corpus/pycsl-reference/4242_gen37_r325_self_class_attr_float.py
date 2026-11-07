r"""Test 4242 -- gen #37 route #325 (expected FAIL): `self.R` of a class attribute 0.5: `% 1 == 0` PROVED through `getattr_c` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    R = 0.5
    #@ ensures \result == 1
    #@ assigns \nothing
    def g(self) -> int:
        if self.R % 1 == 0:
            return 1
        return 0

if __name__ == "__main__":
    assert C().g() == 1
