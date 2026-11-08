r"""Test 7623 -- route #487 (expected FAIL): red-team 40 probe g103_k10306_list_or_neg -- `-(a or a)` (CPython TypeError) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-M6-BOOLOP-VALUE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: List[int]) -> int:
    return -(a or a)


if __name__ == "__main__":
    try:
        r = f([0])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
