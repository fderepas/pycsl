r"""Test 4571 -- gen #37 route #342 (expected FAIL): witness x03: `d.__class__ = C` retypes a `D` (float field) as `C`; `c.r % 1 == 0` PROVED (CPython False). REFUSED (PYCSL-R342-CLASS-REASSIGNMENT, route #342).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 1

class D:
    def __init__(self) -> None:
        self.r = 0.5

#@ ensures \result == True
def f(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    c = C()
    d = D()
    d.__class__ = C
    assert f(d) == True
