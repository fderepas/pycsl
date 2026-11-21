r"""Test 4923 -- gen #37 route #367 (expected FAIL): `__B = 1` (private, mangled, not a member); `C(1)` PROVED (CPython ValueError). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 0
    __B = 1

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(1)
    return 0

if __name__ == "__main__":
    print(f())
