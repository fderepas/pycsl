r"""Test 4345 -- gen #37 route #330 (expected FAIL): `self.s = "ab"` lowers to `{ s = 0 }`: `c.s * 0 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.s = "ab"

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.s * 0 == 0

if __name__ == "__main__":
    assert g() == True, g()
