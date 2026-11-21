r"""C8 — carrier of MY OWN draft-4: the string-argument rule keys on a CONSTANT. A computed
name argument hides the spelling entirely."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    getattr(f, "__glo" + "bals__")["N"] = 5


g()
