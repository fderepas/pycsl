r"""Test 4755 -- gen #37 route #353 (expected FAIL): `class C(M, int, Enum)` with `M.__sub__` -> 1: `x - x` PROVED 0 (CPython 1). REFUSED now (route #353).
"""
# pycsl-expected: FAIL
from enum import Enum

class M:
    def __sub__(self, o: object) -> int:
        return 1

class C(M, int, Enum):
    A = 1

#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    assert f() == 0, f()
