r"""Test 5017 -- gen #37 route #370 (expected FAIL): `_ignore_.append("B")`, `C.B` admitted (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    _ignore_ = []
    _ignore_.append("B")
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B
    return 0

if __name__ == "__main__":
    print(f())
