r"""Test 4932 -- gen #37 route #367 (expected FAIL): enum `__eq__, _x = (lambda ..), 0`; `x == x` proved True (CPython False). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    __eq__, _x = (lambda self, o: False), 0

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    print(f())
