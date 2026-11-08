r"""Test 8444 -- route #529 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1107/bh1008_dstar_strs_init.py): `{**xs}` of a List[str] in a constructor judged by route #519; CPython TypeError: not a mapping
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[str]) -> None:
        self.k = {**xs}


#@ no_exception \all
def f(xs: List[str]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f(["a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
