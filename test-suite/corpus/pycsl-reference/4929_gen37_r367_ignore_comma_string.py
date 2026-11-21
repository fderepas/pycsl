r"""Test 4929 -- gen #37 route #367 (expected FAIL): IntEnum `_ignore_ = "B, D"`; `C(4)` (CPython ValueError). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    _ignore_ = "B, D"
    A = 1
    D = 4

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(4)
    return 0

if __name__ == "__main__":
    print(f())
