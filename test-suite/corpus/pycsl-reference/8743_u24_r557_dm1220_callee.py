r"""Test 8743 -- route #557 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R557-SET-SUBSCRIPT; red team 53 probe g1412/dm1220_callee.py): an item store into a callee's `Set[int]` parameter; CPython TypeError: 'set' object does not support item assignment
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(u: Set[int]) -> None:
    u[0] = 1


@dataclass
class R:
    s: Set[int]



#@ no_exception \all
def f(k: int, s: Set[int], ws: Set[str], xs: List[int], r: R) -> int:
    g(s)
    return 1


if __name__ == "__main__":
    try:
        r = f(1, {1, 2}, {"a"}, [1, 2], R({1}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
