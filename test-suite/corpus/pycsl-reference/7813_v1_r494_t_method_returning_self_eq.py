r"""Test 7813 -- route #494 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): a `\trusted` k tests `o.me() == 1` (`me` returns `self`); the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g308/p3021_me_eq.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    def me(self) -> 'C':
        return self

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __eq__(self, other: object) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __add__(self, x: int) -> int:
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


def ident(x: C) -> C:
    return x


def pick(x: C, y: int) -> C:
    return x


class Box:
    def __init__(self, o: C) -> None:
        self.o = o


#@ \trusted
def k(o: C) -> int:
    return (1 if o.me() == 1 else 0)


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
