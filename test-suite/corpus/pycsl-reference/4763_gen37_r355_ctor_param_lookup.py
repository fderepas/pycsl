r"""Test 4763 -- gen #37 route #355 (expected FAIL): NEW shape: `C(v)` with an `int` parameter under `no_exception \all` PROVED (CPython ValueError for `f(5)`). REFUSED now (route #355).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    A = 1

#@ no_exception \all
def f(v: int) -> int:
    x = C(v)
    return 0

if __name__ == "__main__":
    f(5)
