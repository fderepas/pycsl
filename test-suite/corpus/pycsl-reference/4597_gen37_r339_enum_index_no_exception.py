r"""Test 4597 -- gen #37 route #339 (expected FAIL): plain `Enum` member as a list index `a[x]` under `no_exception \all` PROVED (CPython TypeError). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #339).
"""
# pycsl-expected: FAIL
from enum import Enum
from typing import List

class C(Enum):
    A = 0
    B = 1

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    a: List[int] = [0, 0]
    x = C.A
    if x == x * 0:
        return a[x]
    return 0

if __name__ == "__main__":
    assert f() == 0
