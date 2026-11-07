r"""Test 7016 -- route #452 (expected FAIL): red-team 36 probe c5_y000_bytes_find_int -- `b"abc".find(n)` with `n: int` (CPython ValueError for n = 256). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    return b'abc'.find(n)


if __name__ == "__main__":
    try:
        r = f(300)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
