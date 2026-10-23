r"""P13 — #136: IN-FUNCTION dynamic exec writing a module global (hoare model)."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f(code: str) -> int:
    exec(code, globals())
    return N
