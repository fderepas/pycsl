r"""P18 — module-scope `globals().update(...)` rebinding a folded constant."""
_ = 0  # anchor
N = 3
globals().update({"N": 5})


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
