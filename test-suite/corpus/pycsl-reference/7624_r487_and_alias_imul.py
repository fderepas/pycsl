r"""Test 7624 -- route #487 (expected FAIL): red-team 40 probe g100_z10002_and_imul -- `b = a and a; b *= 2` (CPython extends `a` in place) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-M6-BOOLOP-VALUE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: List[int]) -> int:
    b = a and a
    b *= 2
    return len(a)


if __name__ == "__main__":
    try:
        r = f([0, 0])
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
