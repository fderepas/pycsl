r"""Test 4562 -- gen #37 route #342 (expected FAIL): witness i12: subclass `super().__init__(); setattr(self, "x", 5)`: PROVED (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0

class S(B):
    def __init__(self) -> None:
        super().__init__()
        setattr(self, "x", 5)

#@ no_exception \all
#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(S()) == 0
