r"""P3 (a5) — the #136 eval token rule keys on the eight namespace builtins appearing as
identifiers in the CONSTANT text. `f.__globals__.__setitem__('N', 5)` names none of them."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


eval("f.__globals__.__setitem__('N', 5)")
