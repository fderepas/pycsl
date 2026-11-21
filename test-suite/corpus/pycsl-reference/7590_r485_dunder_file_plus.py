r"""Test 7590 -- route #485 (expected FAIL): red-team 40 probe g86_b9005_dunder_file_plus -- `__file__ + n` under `no_exception \all` (CPython TypeError: str + int) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    return __file__ + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
