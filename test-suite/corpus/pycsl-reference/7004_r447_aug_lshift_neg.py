r"""Test 7004 -- route #447 (expected FAIL): red-team 36 probe c1_o028_aug_lshift_neg -- `a <<= b` with b = -1 (CPython ValueError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
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
        r = f(1, -1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
