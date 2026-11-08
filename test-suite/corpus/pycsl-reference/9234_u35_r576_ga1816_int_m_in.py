r"""Test 9234 -- route #576 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe ga1816_int_m_in.py): `return 1 if k in k.bit_length else 0`; CPython TypeError argument of type 'builtin_function_or_method' is not a container or iterable
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


@dataclass
class P:
    a: int
    s: str



#@ no_exception \all
def f(k: int, xs: List[int], s: str, p: P) -> int:
    return 1 if k in k.bit_length else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2], "ab", P(1, "q")))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
