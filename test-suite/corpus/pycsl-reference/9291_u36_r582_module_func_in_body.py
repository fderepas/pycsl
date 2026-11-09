r"""Test 9291 -- route #582 (expected FAIL: NOT PROVED at base 822621340 only because Why3 rejects the module function's `self: Any` store (a typing error, unrelated), REFUSED PYCSL-R582-CLASS-BODY-ALIAS-CALL in every model at HEAD; red team 55 probe (u36 probe p582d)): a MODULE function bound in the class body (`n = g`, `def g(self, v): self.a = v`) is a method; CPython caller(C()) == 5 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any
def g(self: Any, v: int) -> None:
    self.a = v

from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    n = g


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
