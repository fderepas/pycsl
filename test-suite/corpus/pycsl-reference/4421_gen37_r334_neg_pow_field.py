r"""Test 4421 -- gen #37 route #334 (expected FAIL): a field `self.r = 2 ** -1` (a float, 0.5) was carried as an int and `int(c.r) == c.r` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 2 ** -1

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()

    return int(c.r) == c.r

if __name__ == "__main__":
    assert g() == True, g()
