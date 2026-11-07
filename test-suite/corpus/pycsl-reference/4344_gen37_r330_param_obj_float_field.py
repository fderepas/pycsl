r"""Test 4344 -- gen #37 route #330 (expected FAIL): `self.r = 0.5` read through a parameter `c: C`: `c.r % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 0.5

#@ ensures \result == True
#@ assigns \nothing
def g(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g(C()) == True, g(C())
