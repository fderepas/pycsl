r"""Test 4756 -- gen #37 route #353 (expected FAIL): `class C(M, Base)`, `Base(IntEnum)` member-less, `M.__lt__` -> True: `x < x` PROVED False (CPython True). REFUSED now (route #353).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class M:
    def __lt__(self, o: object) -> bool:
        return True

class Base(IntEnum):
    pass

class C(M, Base):
    A = 1

#@ ensures \result == False
def f() -> bool:
    x = C.A
    return x < x

if __name__ == "__main__":
    assert f() == False, f()
