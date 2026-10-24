r"""Test 4424 -- gen #37 route #334 (expected FAIL): a field `self.r = 10 ** -1` was carried as an int and `c.r * 10 == 1` was decided False (CPython 0.1 * 10 == 1.0 is True). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 10 ** -1

#@ assigns \nothing
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.r * 10 == 1 else 0

if __name__ == "__main__":
    assert g() == 0, g()
