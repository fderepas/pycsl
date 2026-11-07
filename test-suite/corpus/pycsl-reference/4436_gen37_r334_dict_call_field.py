r"""Test 4436 -- gen #37 route #334 (expected FAIL): a dict field `self.d = dict(a=0.5)` had its values read as ints and `c.d["a"] % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.d = dict(a=0.5)

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.d["a"] % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
