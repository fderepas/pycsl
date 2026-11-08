r"""Test 8447 -- route #530 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1100/ba1114_sorted_key_len.py): `sorted(xs, key=len)` of List[int] in a constructor judged by route #519; CPython TypeError: object of type 'int' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[int]) -> None:
        self.k = sorted(xs, key=len)


#@ no_exception \all
def f(xs: List[int]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f([1, 2])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
