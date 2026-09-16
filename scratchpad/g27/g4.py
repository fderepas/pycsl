r"""G4 — carrier of MY OWN #138 repair: the namespace mapping is bound to a plain name (the
one escape the rule allows, for route #116's `_g = globals()` idiom) and then MUTATED inside a
function, where the module-executed sink does not reach."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    d = f.__globals__
    d["N"] = 5


g()
