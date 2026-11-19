r"""Test 7803 -- route #491 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): a `\trusted` k returns `next(iter(o, 2))` (runs `o.__call__`); the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g305/u3004_t_next_iter_sentinel.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __call__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
def k(o: C) -> int:
    return next(iter(o, 2))


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
