r"""Test 5463 -- gen #37 systematic rule S1 (expected PASS): CONTROL: `from enum import Enum as E; class C(int, E)` -- `int` as the mixin of an enum base (route #353's int-mixin enum) and an aliased `enum.Enum` are both in S1's BASE-MODEL table; `x - x == 0` PROVED (CPython 0).
"""
# pycsl-expected: PASS
from enum import Enum as E

class C(int, E):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    assert f() == 0
