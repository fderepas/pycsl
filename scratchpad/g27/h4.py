r"""H4 — carrier of MY OWN #138 namespace-mapping escape rule: the rule permits binding the
mapping to a plain name, and then that NAME is an unguarded handle on the module namespace."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


_g = f.__globals__
dict.update(_g, N=5)
