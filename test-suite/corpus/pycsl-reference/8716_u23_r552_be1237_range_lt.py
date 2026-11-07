r"""Test 8716 -- route #552 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R552-VALUE-KIND-MISMATCH; red team 52 probe g1304/be1237_range_lt.py): `range(k) < range(k)`; CPython f(1) -> TypeError: '<' not supported between instances of 'range' and 'range'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    t: Tuple[int, int]


@dataclass
class P:
    a: int


def g() -> Tuple[int, int]:
    return (1, 1)



#@ no_exception \all
def f(k: int) -> int:
    return 1 if range(k) < range(k) else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
