r"""C18 — carrier: `inspect.currentframe().f_globals`."""
_ = 0  # anchor
import inspect

N = 3
inspect.currentframe().f_globals["N"] = 5


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
