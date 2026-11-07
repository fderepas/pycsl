r"""Test 4565 -- gen #37 route #342 (expected FAIL): witness i20: own `__init__` `setattr(self, "x", 5)` (route #226 "not covered"): PROVED (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        setattr(self, "x", 5)

#@ no_exception \all
#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
