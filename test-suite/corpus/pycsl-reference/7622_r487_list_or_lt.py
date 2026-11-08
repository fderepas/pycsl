r"""Test 7622 -- route #487 (expected FAIL): red-team 40 probe g103_k10302_list_or_lt -- `x = a or a; x < 3` (CPython TypeError list < int) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-M6-BOOLOP-VALUE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: List[int]) -> int:
    x = a or a
    return 1 if x < 3 else 0


if __name__ == "__main__":
    try:
        r = f([0])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
