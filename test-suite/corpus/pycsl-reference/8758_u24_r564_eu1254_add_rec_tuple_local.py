r"""Test 8758 -- route #564 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R564-DISPLAY-ELEMENT-KIND; red team 53 probe g1446/eu1254_add_rec_tuple_local.py): `w = (1, p + p)` of a record without `__add__`; CPython TypeError: unsupported operand type(s) for +: 'P' and 'P'
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
    w = (1, p + p)
    return 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1}, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
