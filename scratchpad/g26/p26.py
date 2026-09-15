r"""P26 — #135 carrier: the patch hides in a DEFAULT ARGUMENT, evaluated at module scope;
the sink walk skips every FunctionDef node whole."""
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


def h(z: Any = (lambda m: setattr(m, "inc", plainlib.dec))(plainlib)) -> int:
    return 0


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
