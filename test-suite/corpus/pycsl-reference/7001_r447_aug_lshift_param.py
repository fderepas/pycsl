r"""Test 7001 -- route #447 (expected FAIL): red-team 36 probe c11_q063_aug_shift_param -- `a <<= b` on a PARAMETER (CPython ValueError, negative shift count). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: int, b: int) -> int:
    a <<= b
    return a


if __name__ == "__main__":
    try:
        r = f(1, -2)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
