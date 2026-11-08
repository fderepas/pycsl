# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    x = 0
    #@ ghost x = 99
    return x
