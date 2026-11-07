r"""Test 5010 -- gen #37 route #370 (expected FAIL): explicit mangled `_C__B = 2` is private, `C(2)` admitted (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    _C__B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(2)
    return 0

if __name__ == "__main__":
    print(f())
