r"""Test 7357 -- route #471 (expected FAIL): red-team 38 witness `g13_k131_namedtuple_underscore` -- a NamedTuple field `_x` inside the claimed def (ValueError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from typing import NamedTuple


#@ no_exception \all
def f(n: int) -> int:
    class P(NamedTuple):
        _x: int
    return n


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
