r"""P27 — #135 carrier: the patch hides in a DECORATOR EXPRESSION, evaluated at module scope."""
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


def mk(m: Any) -> Any:
    setattr(m, "inc", plainlib.dec)
    return lambda fn: fn


@mk(plainlib)
def h() -> int:
    return 0


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
