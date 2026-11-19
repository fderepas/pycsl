r"""Test 8752 -- route #563 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R563-METHOD-ARGUMENT-KIND; red team 53 probe g1446/eu1277_m_str_dict_val.py): a `Dict[str, str]` value passed to `p.m(y: int)`; CPython TypeError: unsupported operand type(s) for +: 'int' and 'str' (in P.m)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y


def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int], p: P) -> int:
    w = {"a": p.m(t)}
    return 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1}, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
