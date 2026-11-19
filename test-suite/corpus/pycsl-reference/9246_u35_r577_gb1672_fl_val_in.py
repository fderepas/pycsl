r"""Test 9246 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R577-ENUM-MEMBER-VALUE-OPERAND; red team 55 probe gb1672_fl_val_in.py): `return 1 if k in FL.R.value else 0`; CPython TypeError argument of type 'int' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2



class FL(enum.IntFlag):
    R = 1
    W = 2



@dataclass
class Q:
    m: IE



#@ no_exception \all
def f(k: int, xs: List[int], s: str, ie: IE, q: Q) -> int:
    return 1 if k in FL.R.value else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2, 3, 4], "ab", IE.A, Q(IE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
