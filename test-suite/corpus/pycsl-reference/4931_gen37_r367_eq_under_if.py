r"""Test 4931 -- gen #37 route #367 (expected FAIL): enum `def __eq__` nested under `if True:`; `x == x` proved True (CPython False). REFUSED now (route #367: class-scope dunders at any nesting).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    if True:
        def __eq__(self, o: object) -> bool:
            return False

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    print(f())
