r"""Test 1378 — ROUTE #135: `m = ident(plainlib); m.inc = plainlib.dec` at MODULE scope; #127's alias taint treated an ordinary call's result as a plain value, and module-scope code is never lowered, so `plainlib.inc(3)` PROVED `\result == 4` while CPython runs `dec` and returns 2. At module and class-body scope an attribute write is now allowed only on a name bound to a literal or to a fresh instance of a class defined in the module.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


def ident(x: Any) -> Any:
    return x


m = ident(plainlib)
m.inc = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
