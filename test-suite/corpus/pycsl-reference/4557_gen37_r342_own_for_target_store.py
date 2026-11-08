r"""Test 4557 -- gen #37 route #342 (expected FAIL): witness i21: own `__init__` `for self.x in range(3)` after `self.x = 0` under invariant `x == 0`: vacuous goal; PROVED (CPython 2). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        for self.x in range(3):
            pass

#@ no_exception \all
#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
