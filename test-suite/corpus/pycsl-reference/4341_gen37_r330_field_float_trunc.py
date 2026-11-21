r"""Test 4341 -- gen #37 route #330 (expected FAIL): `self.r = 2.5` lowers to `{ r = (any int) }`: `int(c.r) == c.r` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 2.5

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return int(c.r) == c.r

if __name__ == "__main__":
    assert g() == True, g()
