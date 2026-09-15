r"""P5 — same, exec of a module string constant."""
_ = 0  # anchor
N = 3
S = "N = 5"
exec(S)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
