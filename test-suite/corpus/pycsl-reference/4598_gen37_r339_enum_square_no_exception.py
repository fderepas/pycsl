r"""Test 4598 -- gen #37 route #339 (expected FAIL): plain `Enum` member `x * x` under `no_exception \all` PROVED `>= 0` (CPython TypeError). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #339).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 2
    B = 3

#@ no_exception \all
#@ ensures \result >= 0
def f() -> int:
    x = C.A
    return x * x

if __name__ == "__main__":
    assert f() >= 0
