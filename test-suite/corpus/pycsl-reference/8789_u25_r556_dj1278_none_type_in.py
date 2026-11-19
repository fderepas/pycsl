r"""Test 8789 -- route #556 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 53 probe g1409/dj1278_none_type_in.py): `return 1 if k in type(None) else 0`; CPython TypeError: argument of type 'type' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math
import os
import functools



#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int]) -> int:
    return 1 if k in type(None) else 0


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
