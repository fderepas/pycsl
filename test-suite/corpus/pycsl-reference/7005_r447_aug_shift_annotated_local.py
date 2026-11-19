r"""Test 7005 -- route #447 (expected FAIL): red-team 36 probe c31_a003_annot -- `c <<= b` on an ANNOTATED local `c: int = a` (CPython ValueError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: int, b: int) -> int:
    c: int = a
    c <<= b
    return 1


if __name__ == "__main__":
    try:
        r = f(1, -1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
