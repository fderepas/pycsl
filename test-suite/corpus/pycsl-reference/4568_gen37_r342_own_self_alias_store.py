r"""Test 4568 -- gen #37 route #342 (expected FAIL): witness i35: own `__init__` `s = self; s.x = 5`: PROVED (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        s = self
        s.x = 5

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
