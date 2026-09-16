r"""C2 — carrier of MY OWN draft-1: the mutating-method sink keys on the RECEIVER of the
method. Spell it as an UNBOUND method on `dict` and the receiver becomes the name `dict`,
which has no module binding and therefore defaults to FRESH."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


dict.__setitem__(f.__globals__, "N", 5)
