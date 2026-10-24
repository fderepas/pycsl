r"""Test 4592 -- gen #37 route #339 (expected FAIL): `IntEnum` with a user `__lt__` returning True: `x < x` PROVED False (CPython True). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #339).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    A = 1
    B = 2

    def __lt__(self, other: object) -> bool:
        return True

#@ ensures \result == False
def f() -> bool:
    x = C.A
    return x < x

if __name__ == "__main__":
    assert f() == False
