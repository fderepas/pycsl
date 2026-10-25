r"""Test 4771 -- gen #37 route #352 (expected PASS): CONTROL: an alias-based plain enum member bound / aliased / compared by `is` proves (CPython True).
"""
# pycsl-expected: PASS
from enum import Enum as E

class C(E):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == True
def f() -> bool:
    x = C.A
    y = x
    return x is y

if __name__ == "__main__":
    assert f() == True
