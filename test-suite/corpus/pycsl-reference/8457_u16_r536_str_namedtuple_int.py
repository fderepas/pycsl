r"""Test 8457 -- route #536 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1109/bj1024_str_nt.py): `str(p)` of a NamedTuple with an int field in a constructor judged by route #519; CPython ValueError: Exceeds the limit (4300 digits)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from typing import NamedTuple


class P(NamedTuple):
    v: int


class C:
    def __init__(self, p: P) -> None:
        self.k = str(p)


#@ no_exception \all
def f(p: P) -> int:
    c = C(p)
    return 1


if __name__ == "__main__":
    try:
        r = f(P(10 ** 5000))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
