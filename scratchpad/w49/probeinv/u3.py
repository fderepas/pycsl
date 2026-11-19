# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s: str = "é"
    return len(s)
