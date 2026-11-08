r"""Test 8203 -- route #516 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 47 probe g822/z8007_field_x_meth): `p.a * p.gb()` (field `a: int`, `gb() -> float`); CPython f(P(10**400, 0.5, "ab"), ...) raises OverflowError
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
    w = p.a * p.gb()
    return 1


if __name__ == "__main__":
    try:
        r = f(P(10**400, 0.5, "ab"), P(10**400, 0.5, "ab"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
