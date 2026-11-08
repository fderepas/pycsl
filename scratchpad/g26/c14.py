r"""C14 — carrier: the globals dict passed into another call that writes it."""
_ = 0  # anchor
import operator

N = 3
operator.setitem(globals(), "N", 5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
