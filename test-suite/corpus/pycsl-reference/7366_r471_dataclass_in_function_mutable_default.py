r"""Test 7366 -- route #471 (expected FAIL): red-team 38 witness `g7_i734_dataclass_in_function_mutable_default` -- a local dataclass with a mutable default (ValueError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    @dataclass
    class P:
        xs: List[int] = []
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
