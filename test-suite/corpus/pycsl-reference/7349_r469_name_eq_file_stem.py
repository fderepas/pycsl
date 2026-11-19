r"""Test 7349 -- route #469 (expected FAIL): red-team 38 witness `g6_s685_name_eq_file_stem` -- `__name__ == <file stem>` divisor (ZeroDivisionError when imported). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R461-IMPORT-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import os

X = 1 // (__name__ == os.path.splitext(os.path.basename(__file__))[0])


#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
