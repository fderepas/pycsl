# pycsl-flags: --memory-model hoare
_ = 0
#@ ghost g = 99
#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    return 0
