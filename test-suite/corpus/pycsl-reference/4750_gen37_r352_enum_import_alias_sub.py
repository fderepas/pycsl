r"""Test 4750 -- gen #37 route #352 (expected FAIL): `from enum import Enum as E; class C(E)`: plain member `x - x` under `no_exception \all` PROVED 0 (CPython TypeError) -- the alias base was not an enum. REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #352).
"""
# pycsl-expected: FAIL
from enum import Enum as E

class C(E):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    f()
