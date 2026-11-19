r"""Test 7200 -- route #464 (expected FAIL): red-team 37 witness `e29_n100_sub_reads_base_private` -- `self.__x` read in subclass D is `self._D__x`, which C's `__init__` (storing `_C__x`) never set. CPython raises AttributeError (private name mangling); PROVED at 33f7ac681; now REFUSED by route #445 over the mangled names.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.__x = n


class D(C):
    def get(self) -> int:
        return self.__x


#@ no_exception \all
def f(n: int) -> int:
    return D(n).get()


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
