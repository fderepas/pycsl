# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    s: str = "ab"
    s = s + "c"
    if len(s) == 2:
        return 7
    return 0
