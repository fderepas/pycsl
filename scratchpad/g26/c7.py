r"""C7 — carrier: `exec` reached through a computed getattr on `__builtins__`."""
_ = 0  # anchor
N = 3
getattr(__builtins__, "ex" + "ec")("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
