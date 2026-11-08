r"""Test 9225 -- route #575 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe gm1644_obj_inst_in.py): `OB = object()`; `return 1 if k in OB else 0`; CPython TypeError argument of type 'object' is not a container or iterable
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

OB = object()


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    return 1 if k in OB else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2]))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
