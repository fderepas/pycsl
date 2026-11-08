r"""Test 4751 -- gen #37 route #352 (expected FAIL): `from enum import IntEnum as IE` + user `__eq__` -> False: `x == x` PROVED True (CPython False). REFUSED now (route #352).
"""
# pycsl-expected: FAIL
from enum import IntEnum as IE

class C(IE):
    A = 1
    B = 2

    def __eq__(self, other: object) -> bool:
        return False
    __hash__ = IE.__hash__

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    assert f() == True, f()
