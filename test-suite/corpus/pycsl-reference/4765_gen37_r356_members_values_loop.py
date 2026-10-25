r"""Test 4765 -- gen #37 route #356 (expected FAIL): `for m in C.__members__.values(): m - m` under `no_exception \all` PROVED (CPython TypeError). REFUSED now (route #356).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1

#@ no_exception \all
def f() -> int:
    n = 0
    for m in C.__members__.values():
        n = m - m
    return n

if __name__ == "__main__":
    f()
