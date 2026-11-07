# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = {1: 10}
    d[2] = 20
    return len(d)
