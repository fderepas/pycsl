r"""C6 — carrier of MY OWN draft-3: the namespace-mapping rule keys on the ATTRIBUTE spelling.
`getattr(f, "__globals__")` names no attribute, and #118's alias walk does not treat a
`getattr` chain rooted at a def as a namespace."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    getattr(f, "__globals__")["N"] = 5


g()
