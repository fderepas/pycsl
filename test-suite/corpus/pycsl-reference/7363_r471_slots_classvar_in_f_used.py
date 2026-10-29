r"""Test 7363 -- route #471 (expected FAIL): red-team 38 witness `g13_k144_slots_classvar_in_f_used` -- `__slots__` vs a class variable inside the claimed def (ValueError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    class Z:
        __slots__ = ('x',)
        x = 1
    return n


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
