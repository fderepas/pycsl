r"""Test 4556 -- gen #37 route #341 (expected FAIL): witness o16: `Base: Type[B] = B`: annotated alias base dropped; PROVED (CPython 2). REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME, route #341).
"""
# pycsl-expected: FAIL
from typing import Type

class B:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

Base: Type[B] = B

class S(Base):
    def m(self) -> int:
        return 2

#@ ensures \result == 1
def g(b: B) -> int:
    return b.m()

if __name__ == "__main__":
    assert g(S()) == 1
