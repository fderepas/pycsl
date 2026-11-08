r"""Test 4570 -- gen #37 route #342 (expected FAIL): witness i39: own `__init__` store inside an `if`: no goal, invariant assumed; PROVED (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        if self.x == 0:
            self.x = 5

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
