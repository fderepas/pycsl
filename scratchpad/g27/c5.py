r"""C5 — carrier of MY OWN draft-2: the `_nb_reach` widening only sees a CONSTANT text. A
DYNAMIC in-function eval carries the same mutation and is still gated on location."""
_ = 0  # anchor
N = 3
S = "f.__globals__.__setitem__('N', 5)"


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    eval(S)


g()
