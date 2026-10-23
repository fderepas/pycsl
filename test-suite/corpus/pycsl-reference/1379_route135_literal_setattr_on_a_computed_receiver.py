r"""Test 1379 — ROUTE #135 (setattr arm): `setattr(ident(plainlib), "inc", plainlib.dec)` at module scope; the literal `"inc"` is not a def of THIS file and the receiver is not a name, so #119's rule (5) let it through and `plainlib.inc(3)` PROVED `\result == 4` while CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


def ident(x: Any) -> Any:
    return x


setattr(ident(plainlib), "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
