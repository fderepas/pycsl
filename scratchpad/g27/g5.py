r"""G5 — carrier of MY OWN #138 repair: `sys.modules[__name__]` is a module object reached
without any of the four namespace attributes, and the patch happens inside a function."""
_ = 0  # anchor
import sys

N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    sys.modules[__name__].N = 5


g()
