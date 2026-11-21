r"""C13 — carrier: `globals().__setitem__("N", 5)` at module scope."""
_ = 0  # anchor
N = 3
globals().__setitem__("N", 5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
