r"""Test 4752 -- gen #37 route #353 (expected FAIL): `class C(M, IntEnum)` with `M.__sub__` -> 1: `x - x` PROVED 0 (CPython 1) -- a non-enum mixin's dunder was unseen. REFUSED now (route #353).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class M:
    def __sub__(self, o: object) -> int:
        return 1

class C(M, IntEnum):
    A = 1
    B = 2

#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    assert f() == 0, f()
