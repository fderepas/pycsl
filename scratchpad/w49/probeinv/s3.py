# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1000
    y = 500 + 500
    if x is y:
        return 7
    return 0
