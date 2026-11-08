r"""P4 — #132/#131 exec-arm carrier: a DYNAMIC (non-constant) exec rebinding a folded constant."""
_ = 0  # anchor
N = 3
exec("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
