r"""Test 7802 -- route #491 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): a `\trusted` k tests `isinstance(1, o)` (runs `C.__instancecheck__`, which writes `self.v`); the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g305/u3005_t_isinstance_cls.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __instancecheck__(self, x: object) -> bool:
        self.v = 7
        return True


#@ \trusted
def k(o: C) -> int:
    return 1 if isinstance(1, o) else 0


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
