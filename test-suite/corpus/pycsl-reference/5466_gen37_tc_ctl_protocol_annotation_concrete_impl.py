r"""Test 5466 -- gen #37 systematic rule TC (expected PASS): CONTROL: a `typing.Protocol` `P` used only as a TYPE (a local's annotation, a class base) and a concrete class `C(P)` (not itself a protocol: `Protocol` is not among its bases) constructed and passed; PROVED (CPython 1).
"""
# pycsl-expected: PASS
from typing import Protocol

class P(Protocol):
    def m(self) -> int:
        ...

class C(P):
    def __init__(self) -> None:
        self.n: int = 1

    #@ ensures \result == 1
    def m(self) -> int:
        return 1

#@ ensures \result == 1
def g(c: C) -> int:
    return c.m()

#@ ensures \result == 1
def h() -> int:
    p: P = C()
    return g(C())

if __name__ == "__main__":
    assert h() == 1
