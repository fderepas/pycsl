r"""Test 7808 -- route #493 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): an `\abstract` `__init__` of another class reads `len(o)`; f calls `K(o)`; the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g306/b30080_init_abstract_len.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

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
    def __abs__(self) -> int:
        self.v = 7
        return 1


class K:
    #@ ensures self.r >= 0
    #@ \abstract
    def __init__(self, x: C) -> None:
        self.r = len(x)


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    _q = K(o)
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
