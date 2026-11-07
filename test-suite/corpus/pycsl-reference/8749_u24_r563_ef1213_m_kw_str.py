r"""Test 8749 -- route #563 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R563-METHOD-ARGUMENT-KIND; red team 53 probe g1431/ef1213_m_kw_str.py): `p.m(y=t)`, a str keyword argument into an int parameter; CPython TypeError: unsupported operand type(s) for +: 'int' and 'str' (in P.m)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y

    def ms(self, s: str) -> int:
        return len(s + "c")

    def ml(self, ys: List[int]) -> int:
        return len(ys)

    def mm(self, y: int) -> int:
        return self.m(y)


class Q:
    def __init__(self, a: int) -> None:
        self.a = a

    def m(self, y: int) -> int:
        return self.a + y



#@ no_exception \all
def f(k: int, xs: List[int], t: str, p: P) -> int:
    return p.m(y=t)


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab", P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
