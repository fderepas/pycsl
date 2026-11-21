r"""Test 8742 -- route #557 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R557-SET-SUBSCRIPT; red team 53 probe g1412/dm1214_set_empty.py): an item store into an empty `set()` local; CPython TypeError: 'set' object does not support item assignment
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Set[int]



#@ no_exception \all
def f(k: int, s: Set[int], ws: Set[str], xs: List[int], r: R) -> int:
    u = set()
    u[0] = 1
    return 1


if __name__ == "__main__":
    try:
        r = f(1, {1, 2}, {"a"}, [1, 2], R({1}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
