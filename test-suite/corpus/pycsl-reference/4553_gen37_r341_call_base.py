r"""Test 4553 -- gen #37 route #341 (expected FAIL): witness o13: `class S(base())`: computed base dropped; override contract never compared; PROVED (CPython 2). REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME, route #341).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

def base() -> type:
    return B

class S(base()):
    def m(self) -> int:
        return 2

#@ ensures \result == 1
def g(b: B) -> int:
    return b.m()

if __name__ == "__main__":
    assert g(S()) == 1
