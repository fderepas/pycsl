# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = 0
    #@ ghost x = 99
    return x
