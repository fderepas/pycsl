r"""Test 4559 -- gen #37 route #342 (expected FAIL): witness i23: own `__init__` `del self.x` under `no_exception \all`: PROVED (CPython AttributeError). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        del self.x

#@ no_exception \all
#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
