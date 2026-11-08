r"""Test 4764 -- gen #37 route #355 (expected FAIL): NEW shape: `class C(str, Enum): A = "1"`; `C(1)` under `no_exception \all` PROVED (CPython ValueError: the stored value is the str). REFUSED now (route #355).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(str, Enum):
    A = "1"

#@ no_exception \all
def f() -> int:
    x = C(1)
    return 0

if __name__ == "__main__":
    f()
