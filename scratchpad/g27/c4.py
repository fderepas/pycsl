r"""C4 — carrier of MY OWN draft-1: the eval refusal only fires for a module-executed eval or
one with an explicit mapping argument. A BARE eval inside a function still reaches the real
module globals when its text MUTATES through a call."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    eval("f.__globals__.__setitem__('N', 5)")


g()
