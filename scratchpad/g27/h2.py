r"""H2 — carrier of gen #26's globals() escape rule AND of MY OWN #138 mutator arm: the
mapping is bound to a plain name (the one escape the rule allows) and then passed to an
UNBOUND dict method, whose receiver is the name `dict`."""
_ = 0  # anchor
N = 3
_g = globals()
dict.update(_g, N=5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
