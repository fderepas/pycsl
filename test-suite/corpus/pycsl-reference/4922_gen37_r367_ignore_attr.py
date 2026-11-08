r"""Test 4922 -- gen #37 route #367 (expected FAIL): `_ignore_ = ["B"]`; `x = C.B` PROVED (CPython AttributeError: ignored names are deleted). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    _ignore_ = ["B"]
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == True
def f() -> bool:
    x = C.B
    return x is x

if __name__ == "__main__":
    print(f())
