r"""Test 9214 -- route #575 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe ga1674_cls_of_inst_sumgen.py): `return sum(1 for x in p.__class__)`; CPython TypeError 'type' object is not iterable
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
    return sum(1 for x in p.__class__)


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2], "ab", P(1, "q")))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
