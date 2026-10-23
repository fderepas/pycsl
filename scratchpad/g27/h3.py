r"""H3 — same, via a module function that takes the mapping as an argument."""
_ = 0  # anchor
import operator

N = 3
_g = globals()
operator.setitem(_g, "N", 5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
