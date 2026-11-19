r"""Test 4425 -- gen #37 route #334 (expected FAIL): a None field through a local (`x = None; self.r = x`) was carried as an int and `no_exception` + `c.r * 0 == 0` PROVED (CPython TypeError). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        x = None
        self.r = x

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.r * 0

if __name__ == "__main__":
    assert g() == 0, g()
