r"""C15 — carrier: `dict.update(globals(), N=5)`."""
_ = 0  # anchor
N = 3
dict.update(globals(), N=5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
