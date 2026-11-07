r"""Test 8784 -- route #556 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 53 probe g1407/dh1260_math_in.py): `return 1 if k in math else 0`; CPython TypeError: argument of type 'module' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math
import os



#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    return 1 if k in math else 0


if __name__ == "__main__":
    try:
        r = f(1, [1, 2])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
