r"""Test 5015 -- gen #37 route #370 (expected FAIL): `types.DynamicClassAttribute(..)` read as `C.B` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from enum import Enum
import types

class C(Enum):
    A = 1
    B = types.DynamicClassAttribute(lambda s: 1)

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B
    return 0

if __name__ == "__main__":
    print(f())
