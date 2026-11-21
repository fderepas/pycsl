r"""Test 4433 -- gen #37 route #334 (expected FAIL): a field bound as a `for` target (`for self.r in [2.5]`) was carried as an int and `c.r % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        for self.r in [2.5]:
            pass

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
