r"""C17 — carrier: a module def's `__globals__` mapping."""
_ = 0  # anchor
N = 3


#@ ensures \result == N
#@ assigns \nothing
def f() -> int:
    return N


f.__globals__["N"] = 5
