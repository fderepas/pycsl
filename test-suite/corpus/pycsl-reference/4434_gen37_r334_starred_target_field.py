r"""Test 4434 -- gen #37 route #334 (expected FAIL): a field rebound by a starred tuple target (`self.r, *self.t = 2.5, 1`) was carried as an int and `c.r % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 1
        self.r, *self.t = 2.5, 1

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
