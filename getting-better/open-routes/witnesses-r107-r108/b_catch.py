# pycsl-flags: --memory-model hoare
"""ROUTE #107-B — a callee raise in an `else:` block is CAUGHT by the enclosing try,
which Python does not do. The callee is named `boom` so its name contributes no "raise"
substring and the drop of #107-A cannot be what fires.
"""


#@ raises ValueError when x0 < 0
#@ ensures \result >= 0
def boom(x0: int) -> int:
    if x0 < 0:
        raise ValueError("neg")
    return x0


#@ assigns \nothing
def wrapper(k: int) -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        boom(k)
    return y


#@ no_exception ValueError
def caller(k: int) -> int:
    return wrapper(k)
