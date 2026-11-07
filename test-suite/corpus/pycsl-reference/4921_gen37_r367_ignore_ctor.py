r"""Test 4921 -- gen #37 route #367 (expected FAIL): `_ignore_ = ["B"]; B = 2`; `C(2)` under `no_exception \all` PROVED (CPython ValueError). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    _ignore_ = ["B"]
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(2)
    return 0

if __name__ == "__main__":
    print(f())
