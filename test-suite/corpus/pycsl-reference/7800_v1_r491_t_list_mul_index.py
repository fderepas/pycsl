r"""Test 7800 -- route #491 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): a `\trusted` k returns `len([1] * o)` (sequence repetition runs `o.__index__`, which writes `self.v`); the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g301/q3000_t_index_list_mul_r.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __index__(self) -> int:
        self.v = 7
        return 0


#@ \trusted
def k(o: C) -> int:
    return len([1] * o)


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
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
