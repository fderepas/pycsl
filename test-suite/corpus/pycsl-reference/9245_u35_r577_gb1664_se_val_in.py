r"""Test 9245 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R577-ENUM-MEMBER-VALUE-OPERAND; red team 55 probe gb1664_se_val_in.py): `return 1 if k in SE.A.value else 0`; CPython TypeError 'in <string>' requires string as left operand, not int
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2



class SE(enum.Enum):
    A = "aa"
    B = "bb"



@dataclass
class Q:
    m: IE



#@ no_exception \all
def f(k: int, xs: List[int], s: str, ie: IE, q: Q) -> int:
    return 1 if k in SE.A.value else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2, 3, 4], "ab", IE.A, Q(IE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
