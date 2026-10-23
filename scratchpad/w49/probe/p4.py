# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = (1, 2)
    if len(x) == 0:
        return 7
    return 0
