r"""C10 — carrier of my #136 arm: a CONSTANT `eval` whose text has no walrus but whose
EXPRESSION binds — `eval("globals().update({'N': 5})")`."""
_ = 0  # anchor
N = 3
eval("globals().update({'N': 5})")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
