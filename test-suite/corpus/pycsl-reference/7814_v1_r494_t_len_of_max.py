r"""Test 7814 -- route #494 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): a `\trusted` k returns `len(max(o, o))` (`max` returns `o` itself; C's ordering dunders are pure); the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g309/y400_max_two_ordered_len.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns \nothing
    def __gt__(self, other: object) -> bool:
        return False

    #@ assigns \nothing
    def __lt__(self, other: object) -> bool:
        return False

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __add__(self, x: int) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __bool__(self) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __neg__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
def k(o: C) -> int:
    return len(max(o, o))


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
