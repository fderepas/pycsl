r"""P19 — module-scope `vars()[...]` rebinding a folded constant."""
_ = 0  # anchor
N = 3
vars()["N"] = 5


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
