r"""Test 8202 -- route #516 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 47 probe g822/z8000_mul): `p.ga() * p.gb()` (`-> int` / `-> float`) and `self.ga() * self.gb()`: method results were of unknown kind; CPython f(P(10**400, 0.5, "ab"), ...) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int
    b: float
    s: str

    def ga(self) -> int:
        return self.a

    def gb(self) -> float:
        return self.b

    def gs(self) -> str:
        return self.s

    #@ no_exception \all
    def m(self) -> int:
        w = self.ga() * self.gb()
        return 1


#@ no_exception \all
def f(p: P, q: P) -> int:
    w = p.ga() * p.gb()
    return 1


if __name__ == "__main__":
    try:
        r = f(P(10**400, 0.5, "ab"), P(10**400, 0.5, "ab"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
