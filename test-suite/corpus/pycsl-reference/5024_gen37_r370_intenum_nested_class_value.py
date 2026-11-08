r"""Test 5024 -- gen #37 route #370 (expected FAIL): IntEnum nested class read as `C.B.value` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    A = 1
    class B:
        pass

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B.value
    return 0

if __name__ == "__main__":
    print(f())
