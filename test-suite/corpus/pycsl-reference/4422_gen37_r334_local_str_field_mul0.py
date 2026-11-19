r"""Test 4422 -- gen #37 route #334 (expected FAIL): a str field through a local (`x = "ab"; self.s = x`) was carried as an int and `c.s * 0 == 0` PROVED (CPython "" != 0). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        x = "ab"
        self.s = x

#@ assigns \nothing
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.s * 0

if __name__ == "__main__":
    assert g() == 0, g()
