r"""Test 4868 -- gen #37 route #363 (expected FAIL): witness r35: `super(A, self).__init__()` in `B(A)` runs `object.__init__`; `b.x` read under `no_exception \all` PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #363).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.x = 1

class B(A):
    def __init__(self) -> None:
        self.n = 0
        super(A, self).__init__()

#@ no_exception \all
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    print(f(B()))
