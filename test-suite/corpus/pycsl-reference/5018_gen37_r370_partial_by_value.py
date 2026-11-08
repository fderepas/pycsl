r"""Test 5018 -- gen #37 route #370 (expected FAIL): `functools.partial(int)` read as `C.B.name` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import Enum
import functools

class C(Enum):
    A = 1
    B = functools.partial(int)

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B.name
    return 0

if __name__ == "__main__":
    print(f())
