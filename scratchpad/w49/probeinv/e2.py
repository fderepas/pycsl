# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = {1: 10}
    if True in d:
        return 0
    return 7
