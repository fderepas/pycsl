r"""Test 7953 -- route #501 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's `math.sqrt(n)`; the program defines a free `sqrt`; f catches ValueError; CPython returns 2 (red team 45 probe g600/a60004_free_fn_named_sqrt_math_sqrt.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math


#@ ensures \result == 0
def sqrt(x: int) -> int:
    return 0


#@ ensures \result == 1
def g(n: int) -> int:
    y = math.sqrt(n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f(-1)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
