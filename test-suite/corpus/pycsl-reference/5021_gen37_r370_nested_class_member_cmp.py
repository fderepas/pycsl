r"""Test 5021 -- gen #37 route #370 (expected FAIL): nested class read as `C.B.name` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    class B:
        pass

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B.name
    return 0

if __name__ == "__main__":
    print(f())
