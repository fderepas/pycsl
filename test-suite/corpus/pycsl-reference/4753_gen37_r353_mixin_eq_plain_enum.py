r"""Test 4753 -- gen #37 route #353 (expected FAIL): `class C(M, Enum)` with `M.__eq__` -> False: `x == x` PROVED True (CPython False). REFUSED now (route #353).
"""
# pycsl-expected: FAIL
from enum import Enum

class M:
    def __eq__(self, o: object) -> bool:
        return False
    __hash__ = object.__hash__

class C(M, Enum):
    A = 1
    B = 2

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    assert f() == True, f()
