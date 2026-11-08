r"""Test 4869 -- gen #37 route #363 (expected FAIL): witness r42: `super(M, self).__init__()` in `B(M(A))` runs `A.__init__`; `b.m` read PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #363).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.x = 1

class M(A):
    def __init__(self) -> None:
        super().__init__()
        self.m = 0

class B(M):
    def __init__(self) -> None:
        super(M, self).__init__()
        self.n = 0

#@ no_exception \all
def f(b: B) -> int:
    return b.m

if __name__ == "__main__":
    print(f(B()))
