r"""Test 4569 -- gen #37 route #342 (expected FAIL): witness i38: own `__init__` store inside a `while`: no goal, invariant assumed; PROVED (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        while self.x < 5:
            self.x = self.x + 1

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
