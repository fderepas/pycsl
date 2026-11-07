r"""Test 8760 -- route #564 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R564-DISPLAY-ELEMENT-KIND; red team 53 probe g1445/et1257_neg_list_tuple_elt.py): `(1, -xs)` of a list in a tuple display; CPython TypeError: bad operand type for unary -: 'list'
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
    w = (1, -xs)
    return 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1}, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
