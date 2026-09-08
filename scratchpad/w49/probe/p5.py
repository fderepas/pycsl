# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = {1: 2}
    if d[1] == 0:
        return 7
    return 0
