r"""Test 7946 -- route #500 (control, expected PASS): the same method written with ONE tail `return` (a result variable assigned in each branch) is spliced faithfully; CPython 11
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v: int = 0

    def m(self, n: int) -> int:
        r = 2
        if n > 0:
            r = 1
        return r


g = C()


#@ ensures \result == 11
def f(n: int) -> int:
    r = g.m(5)
    return r + 10


if __name__ == "__main__":
    assert f(0) == 11
