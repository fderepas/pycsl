r"""Test 4766 -- gen #37 route #356 (expected FAIL): NEW shape: `for m in C._value2member_map_.values(): m - m` PROVED (CPython TypeError). REFUSED now (route #356).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1

#@ no_exception \all
def f() -> int:
    n = 0
    for m in C._value2member_map_.values():
        n = m - m
    return n

if __name__ == "__main__":
    f()
