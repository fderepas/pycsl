# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = {1: 10, 2: 20}
    del d[1]
    return len(d)
