r"""Test 4762 -- gen #37 route #355 (expected FAIL): `C(99)` on a plain Enum under `no_exception \all` PROVED (CPython ValueError). REFUSED now (route #355).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1

#@ no_exception \all
def f() -> int:
    x = C(99)
    return 0

if __name__ == "__main__":
    f()
