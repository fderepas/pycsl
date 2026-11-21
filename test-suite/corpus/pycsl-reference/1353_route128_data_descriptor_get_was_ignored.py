r"""Test 1353 — ROUTE #128: a DATA DESCRIPTOR (`__get__` -> 7, `__set__` -> no-op) bound as a class attribute intercepts `self.x = 42` and `c.x`; the model read the store back and PROVED `\result == 42` while CPython returns 7. A class defining the descriptor protocol is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any


class Seven:
    def __get__(self, obj: Any, tp: Any = None) -> int:
        return 7

    def __set__(self, obj: Any, val: int) -> None:
        pass


class C:
    x = Seven()

    def __init__(self) -> None:
        self.x = 42


#@ ensures \result == 42
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.x
