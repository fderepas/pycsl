r"""Test 7592 -- route #485 (expected FAIL): red-team 40 probe g90_d9400_file_lt -- `__file__ < n` (CPython TypeError) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    return 1 if __file__ < n else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
