r"""Test 9215 -- route #575 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe ga1682_type_call_sumgen.py): `return sum(1 for x in type(p))`; CPython TypeError 'type' object is not iterable
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
    return sum(1 for x in type(p))


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2], "ab", P(1, "q")))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
