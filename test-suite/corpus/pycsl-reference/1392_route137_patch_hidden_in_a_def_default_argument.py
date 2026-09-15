r"""Test 1392 — ROUTE #137: a def's DEFAULT ARGUMENT (like its annotations and its decorator expressions) is evaluated at DEFINITION time, i.e. at module scope — but route #135's sink walk `continue`d on the whole `FunctionDef` node. The default's patch PROVED `plainlib.inc(3) == 4`; CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any
import multi_file_lib.r119_plainlib as plainlib


def h(z: Any = (lambda m: setattr(m, "inc", plainlib.dec))(plainlib)) -> int:
    return 0


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
