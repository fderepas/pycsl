r"""Test 7142 -- route #461 (expected FAIL): red-team 37 witness `e12_m016_slots_dup_layout` -- two `__slots__` bases (CPython TypeError: lay-out conflict); the module IMPORT raises, so the claimed `f` never runs. PROVED at base 370db7dc2 under `#@ no_exception \all`; now REFUSED (PYCSL-R461-IMPORT-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class A:
    __slots__ = ('a',)


class B:
    __slots__ = ('b',)


class Z(A, B):
    pass



#@ no_exception \all
def f(d: Dict[str, int], xs: List[int], n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f({}, [], 1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
