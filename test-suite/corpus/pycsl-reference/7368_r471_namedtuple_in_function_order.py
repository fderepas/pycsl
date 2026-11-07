r"""Test 7368 -- route #471 (expected FAIL): red-team 38 witness `g7_i738_namedtuple_in_function_order` -- a local NamedTuple with a non-default field after a default (TypeError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from typing import NamedTuple


#@ no_exception \all
def f(n: int) -> int:
    class P(NamedTuple):
        x: int = 0
        y: int
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
