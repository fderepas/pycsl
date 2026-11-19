r"""Test 4924 -- gen #37 route #367 (expected FAIL): IntEnum `_ignore_ = "B"`; `C(2)` PROVED (CPython ValueError). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    _ignore_ = "B"
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(2)
    return 0

if __name__ == "__main__":
    print(f())
