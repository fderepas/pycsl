r"""Test 4423 -- gen #37 route #334 (expected FAIL): a field `self.r = (y := 2.5)` was carried as an int and `int(c.r) == c.r` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = (y := 2.5)

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if int(c.r) == c.r else 0

if __name__ == "__main__":
    assert g() == 1, g()
