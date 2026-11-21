r"""Test 8741 -- route #557 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R557-SET-SUBSCRIPT; red team 53 probe g1405/df1206_fset_store.py): `fs[0] = 1` on a `FrozenSet[int]` parameter; CPython TypeError: 'frozenset' object does not support item assignment
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int


def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, xs: List[int], s: Set[int], d: Dict[str, int], t: str, p: P, fs: FrozenSet[int]) -> int:
    fs[0] = 1
    return 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], {1, 2}, {"a": 1}, "ab", P(1), frozenset({1}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
