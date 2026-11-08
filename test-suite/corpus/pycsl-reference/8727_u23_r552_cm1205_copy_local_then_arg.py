r"""Test 8727 -- route #552 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R552-VALUE-KIND-MISMATCH; red team 52 probe g1338/cm1205_copy_local_then_arg.py): `w = xs.copy(); gi(w)` into an imported `def g(x: int)`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from multi_file_lib.u23_dep552 import g as gi


class Q:
    def __init__(self) -> None:
        self.a = 1

    def m(self, x: int) -> int:
        return x * 2


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int], s: str) -> int:
    w = xs.copy()
    return gi(w)


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1}, "a b")
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
