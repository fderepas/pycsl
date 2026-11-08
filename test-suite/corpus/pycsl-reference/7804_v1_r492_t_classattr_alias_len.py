r"""Test 7804 -- route #492 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): `__len__ = _l` binds a writing method by class-attribute alias; a `\trusted` k returns `len(o)`; the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g301/q3100_t_alias_len.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def _l(self) -> int:
        self.v = 7
        return 1

    __len__ = _l


#@ \trusted
def k(o: C) -> int:
    return len(o)


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
