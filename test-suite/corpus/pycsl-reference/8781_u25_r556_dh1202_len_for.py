r"""Test 8781 -- route #556 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 53 probe g1407/dh1202_len_for.py): `for x in len: c += 1`; CPython TypeError: 'builtin_function_or_method' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math
import os



#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    c = 0
    for x in len:
        c += 1
    return c


if __name__ == "__main__":
    try:
        r = f(1, [1, 2])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
