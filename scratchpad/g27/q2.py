r"""Q2 — the namespace dict reached through a module def's `__globals__` and MUTATED BY A
METHOD CALL, not by a subscript store: draft-9 keyed the SUBSCRIPT sink on the path."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


f.__globals__.__setitem__("N", 5)
