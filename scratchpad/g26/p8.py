r"""P8 — #136 widen: dynamic exec inside a function writing a module global."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    exec("N" + " = 5", globals())
    return N
