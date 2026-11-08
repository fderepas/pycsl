r"""Test 7003 -- route #447 (expected FAIL): red-team 36 probe c11_q065_aug_shift_huge -- `c <<= b` with a count past sys.maxsize (CPython OverflowError, route #414 row). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(b: int) -> int:
    c = 1
    c <<= b
    return 1


if __name__ == "__main__":
    try:
        r = f(2**63)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
