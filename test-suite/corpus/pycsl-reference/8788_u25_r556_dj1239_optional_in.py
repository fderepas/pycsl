r"""Test 8788 -- route #556 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 53 probe g1409/dj1239_optional_t_in.py): `return 1 if k in Optional else 0`; CPython TypeError: argument of type '_SpecialForm' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math
import os
import functools



#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int]) -> int:
    return 1 if k in Optional else 0


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
