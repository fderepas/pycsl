r"""Test 4552 -- gen #37 route #341 (expected FAIL): witness o11: alias base: inherited class invariant `x == 0` dropped, subclass stores 5; PROVED (CPython 5). REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME, route #341).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0

Base = B

class S(Base):
    def __init__(self) -> None:
        self.x = 5

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(S()) == 0
