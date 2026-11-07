r"""Test 7000 -- route #447 (expected FAIL): red-team 36 probe c11_q060_realistic_mask -- `mask <<= width` on a local with `width: int` (CPython ValueError for width = -1). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(width: int) -> int:
    mask = 1
    mask <<= width
    return mask - 1


if __name__ == "__main__":
    try:
        r = f(-1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
