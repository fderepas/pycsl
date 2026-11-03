r"""Test 8446 -- route #530 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1100/ba1112_sorted_any.py): `sorted(xs)` of List[Any] in a constructor judged by route #519; CPython TypeError: '<' not supported
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[Any]) -> None:
        self.k = sorted(xs)


#@ no_exception \all
def f(xs: List[Any]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f([1, "a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
