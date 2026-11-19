r"""Test 9292 -- route #582 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R582-CLASS-BODY-ALIAS-CALL in every model; red team 55 probe (u36 probe p582e)): an ANNOTATED class-body alias `n: Any = m`; CPython caller(C()) == 5 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    n: Any = m


#@ requires c.a == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: C) -> int:
    c.n(5)
    return c.a



if __name__ == "__main__":
    try:
        r = caller(C())
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
