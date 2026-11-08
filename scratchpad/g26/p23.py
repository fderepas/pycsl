r"""P23 — #135 carrier: a module-scope CALL of a def that patches through its parameter."""
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


def patch(m: Any) -> None:
    setattr(m, "inc", plainlib.dec)


patch(plainlib)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
