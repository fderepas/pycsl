r"""Test 4550 -- gen #37 route #341 (expected FAIL): witness o09: alias `Base = B; class S(Base)`: the float override of `-> int` escaped R5 (S unrelated to B); `b.m() % 1 == 0` PROVED (CPython False). REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME, route #341).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.n = 1
    def m(self) -> int:
        return 1

Base = B

class S(Base):
    def m(self) -> float:
        return 0.5

#@ ensures \result == True
def g(b: B) -> bool:
    return b.m() % 1 == 0

if __name__ == "__main__":
    assert g(S()) == True
