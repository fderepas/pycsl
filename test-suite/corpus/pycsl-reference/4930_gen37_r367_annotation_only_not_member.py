r"""Test 4930 -- gen #37 route #367 (expected FAIL): `B: int` (annotation without value binds nothing); `x = C.B` (CPython AttributeError). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    B: int

#@ no_exception \all
#@ ensures \result == True
def f() -> bool:
    x = C.B
    return x is x

if __name__ == "__main__":
    print(f())
