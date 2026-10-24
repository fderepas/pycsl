r"""Test 4593 -- gen #37 route #339 (expected FAIL): plain `Enum` member `x < x` under `no_exception \all` PROVED (CPython TypeError). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #339).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == False
def f() -> bool:
    x = C.A
    return x < x

if __name__ == "__main__":
    assert f() == False
