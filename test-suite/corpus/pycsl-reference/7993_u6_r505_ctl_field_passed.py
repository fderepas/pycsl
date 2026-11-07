r"""Test 7993 -- route #505 (control, expected PASS, the advice): the spliced method passes the FIELD (`getv(self.v)`), not `self`; claimed g.v; CPython 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self, v: int) -> None:
        self.v = v

    def m(self) -> int:
        return getv(self.v)


#@ ensures \result == v
def getv(v: int) -> int:
    return v


g = C(1)


#@ ensures \result == g.v
def f(n: int) -> int:
    return g.m()


if __name__ == "__main__":
    assert f(0) == 1
