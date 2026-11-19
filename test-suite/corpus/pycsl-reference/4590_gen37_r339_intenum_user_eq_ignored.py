r"""Test 4590 -- gen #37 route #339 (expected FAIL): `IntEnum` with a user `__eq__` returning False: `x == x` PROVED True (CPython False). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #339).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    A = 1
    B = 2

    def __eq__(self, other: object) -> bool:
        return False
    __hash__ = IntEnum.__hash__

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    assert f() == True
