r"""Test 7367 -- route #471 (expected FAIL): red-team 38 witness `g7_i737_enum_in_function_dup` -- a local Enum with a duplicate member (TypeError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import enum


#@ no_exception \all
def f(n: int) -> int:
    class E(enum.Enum):
        A = 1
        A = 2
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
