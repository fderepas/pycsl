r"""P14 — #136: IN-FUNCTION eval with a walrus writing a module global (hoare model)."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    eval("(N := 5)", globals())
    return N
