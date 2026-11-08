r"""Test 5020 -- gen #37 route #370 (expected FAIL): IntEnum explicit `_C__B = 2`, `C(2)` admitted (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    A = 1
    _C__B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(2)
    return 0

if __name__ == "__main__":
    print(f())
