r"""Test 7593 -- route #485 (expected FAIL): red-team 40 probe g90_d9404_file_ens_value -- `ensures \result == 0` of `__file__ * 0` (CPython returns the empty str) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == 0
def f(n: int) -> int:
    return __file__ * 0


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
