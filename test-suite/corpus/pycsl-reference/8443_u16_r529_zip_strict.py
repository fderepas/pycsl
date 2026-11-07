r"""Test 8443 -- route #529 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1100/ba1143_zip_strict.py): `list(zip(xs, ys, strict=True))` in a constructor judged by route #519; CPython ValueError (zip lengths differ)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[int], ys: List[int]) -> None:
        self.k = list(zip(xs, ys, strict=True))


#@ no_exception \all
def f(xs: List[int], ys: List[int]) -> int:
    c = C(xs, ys)
    return 1


if __name__ == "__main__":
    try:
        r = f([1], [])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
