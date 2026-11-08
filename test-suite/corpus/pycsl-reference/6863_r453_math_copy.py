r"""Test 6863 -- route #453 (expected FAIL): red team 36 witness `witnesses-r453/c25_t003_math_copy.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `math.copy(n)` (no such function) admitted by the tail `copy`; CPython AttributeError. Refused PYCSL-R453-MODULE-ATTRIBUTE.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import math



#@ no_exception \all
def f(n: int) -> int:
    y = math.copy(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
