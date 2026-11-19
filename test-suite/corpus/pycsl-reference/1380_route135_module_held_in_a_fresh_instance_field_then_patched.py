r"""Test 1380 — ROUTE #135 (chain arm, order 2): `m = H(plainlib)` stores the module in a field and `m.x.inc = plainlib.dec` patches it at module scope; the first repair draft accepted any chain rooted at a fresh instance, and `plainlib.inc(3)` PROVED `\result == 4` while CPython returns 2. The receiver of a module-scope attribute write must now BE the fresh name.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


class H:
    def __init__(self, mod: Any) -> None:
        self.x = mod


m = H(plainlib)
m.x.inc = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
