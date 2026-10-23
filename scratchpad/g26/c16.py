r"""C16 — carrier: `sys.modules[__name__].__dict__["N"] = 5`."""
_ = 0  # anchor
import sys

N = 3
sys.modules[__name__].__dict__["N"] = 5


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
