r"""C3 — carrier of MY OWN draft-1: `operator.setitem` is not in `_nb_mutators`, and the
namespace reaches it as an ARGUMENT, not as a receiver."""
_ = 0  # anchor
import operator

N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


operator.setitem(f.__globals__, "N", 5)
