r"""Test 9227 -- route #575 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe gm1605_len_alias_for.py): `L = len`; `t = 0; for x in L: t += 1`; CPython TypeError 'builtin_function_or_method' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import os
import os as O
import math
import enum


def h(x: int) -> int:
    return x + 1


class IE(enum.IntEnum):
    A = 1


class EE(enum.Enum):
    A = 1
    S = "ab"

L = len


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    t = 0
    for x in L:
        t += 1
    return t


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2]))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
