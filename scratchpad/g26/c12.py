r"""C12 — carrier: a dynamic exec in a CLASS BODY (bare, one argument)."""
_ = 0  # anchor
N = 3


class K:
    exec("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
