r"""Test 8445 -- route #529 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1107/bh1032_comp_nested_int_init.py): `[y for x in xs for y in x]` over List[int] in a constructor judged by route #519; CPython TypeError: 'int' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[int]) -> None:
        self.k = [y for x in xs for y in x]


#@ no_exception \all
def f(xs: List[int]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
