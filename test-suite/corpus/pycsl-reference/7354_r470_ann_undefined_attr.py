r"""Test 7354 -- route #470 (expected FAIL): red-team 38 witness `g6_s677_ann_undefined_attr` -- an annotation `os.zz_none` read through `__annotations__` (AttributeError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R461-IMPORT-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import os


def g(x: os.zz_none) -> int:
    return 1


X = g.__annotations__


#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
