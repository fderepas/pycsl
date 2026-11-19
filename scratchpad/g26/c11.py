r"""C11 — carrier: a CONSTANT `eval` whose text calls `exec`."""
_ = 0  # anchor
N = 3
eval("exec('N = 5')")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
