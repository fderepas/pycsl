r"""Test 7145 -- route #461 (expected FAIL): red-team 37 witness `e15_c017_init_subclass_called` -- a base whose `__init_subclass__` raises KeyError when the subclass is created; the module IMPORT raises, so the claimed `f` never runs. PROVED at base 370db7dc2 under `#@ no_exception \all`; now REFUSED (PYCSL-R461-IMPORT-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class B:
    def __init_subclass__(cls) -> None:
        v = {}['k']


class Z(B):
    pass



#@ no_exception \all
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
