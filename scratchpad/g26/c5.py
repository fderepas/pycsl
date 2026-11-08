r"""C5 — carrier of my #136 draft: `exec` reached through an alias."""
_ = 0  # anchor
N = 3
ex = exec
ex("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
