r"""Test 7994 -- route #505 (control, expected PASS, the advice): `m(self): return getv(self)` called on a LOCAL instance is verified by its contract, not spliced; claimed 2; CPython 2
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self, v: int) -> None:
        self.v = v

    #@ ensures \result == self.v
    def m(self) -> int:
        return getv(self)


#@ ensures \result == c.v
def getv(c: C) -> int:
    return c.v


#@ ensures \result == 2
def f(n: int) -> int:
    c = C(2)
    return c.m()


if __name__ == "__main__":
    assert f(0) == 2
