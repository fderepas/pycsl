r"""Test 9211 -- route #575 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe ga1608_alias_loc_in.py): `c = KI; return 1 if k in c else 0`; CPython TypeError argument of type 'type' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum
import os
import sys
import string
import functools
import builtins
import typing


class KI:
    def __init__(self, a: int) -> None:
        self.a = a



@dataclass
class P:
    a: int
    s: str



#@ no_exception \all
def f(k: int, xs: List[int], s: str, p: P) -> int:
    c = KI
    return 1 if k in c else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2], "ab", P(1, "q")))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
