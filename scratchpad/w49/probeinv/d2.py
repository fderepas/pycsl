# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    d = {1: 10, True: 20}
    return d[1]
