r"""Test 4560 -- gen #37 route #342 (expected FAIL): witness i24: own `__init__` `with open(..) as self.x`: PROVED (CPython a file object). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        with open("/dev/null") as self.x:
            pass

#@ no_exception \all
#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
