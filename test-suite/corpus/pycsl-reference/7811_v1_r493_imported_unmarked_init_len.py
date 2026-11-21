r"""Test 7811 -- route #493 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): an IMPORTED un-marked class K (multi_file_lib/v1_h493a.py) whose `__init__` stores `self.r = len(o)`; f calls `K(o)`; the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g304/c3200_imported_unmarked_init_len.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from multi_file_lib.v1_h493a import K


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __str__(self) -> str:
        self.v = 7
        return 'c'

    #@ assigns self.v
    def __bool__(self) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __int__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __neg__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __getitem__(self, i: int) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __index__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __eq__(self, other: object) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __lt__(self, other: object) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __format__(self, spec: str) -> str:
        self.v = 7
        return 'c'

    #@ assigns self.v
    def __abs__(self) -> int:
        self.v = 7
        return 1




#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    K(o)
    return o.v


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
