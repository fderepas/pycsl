r"""Test 9154 -- route #569 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 54 probe fd1900_os_sep_int_in.py): `return 1 if k in os.sep else 0`; CPython TypeError: 'in <string>' requires string as left operand, not int
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum
import math
import os
import functools
class IE(enum.IntEnum):
    A = 1
    B = 2
class FL(enum.IntFlag):
    R = 1
    W = 2
class SE(enum.StrEnum):
    S = "ab"
class KI:
    def __init__(self, a: int) -> None:
        self.a = a
@dataclass
class P:
    a: int
def h(x: int) -> int:
    return x + 1

#@ no_exception \all
def f(k: int, xs: List[int], s: str, ki: KI) -> int:
    return 1 if k in os.sep else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2], "ab", KI(1)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
