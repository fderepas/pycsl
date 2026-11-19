r"""Test 4927 -- gen #37 route #367 (expected FAIL): `__B = 1`; `x = C.__B` outside the class (CPython AttributeError: the name is mangled). REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 0
    __B = 1

#@ no_exception \all
#@ ensures \result == True
def f() -> bool:
    x = C.__B
    return x is x

if __name__ == "__main__":
    print(f())
