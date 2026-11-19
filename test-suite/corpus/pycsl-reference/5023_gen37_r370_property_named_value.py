r"""Test 5023 -- gen #37 route #370 (expected FAIL): `B = property(..)` read as `C.B.value` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    B = property(lambda s: 1)

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B.value
    return 0

if __name__ == "__main__":
    print(f())
