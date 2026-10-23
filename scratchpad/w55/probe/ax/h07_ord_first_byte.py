# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 226
#@ assigns \nothing
def f() -> int:
    return ord("€")
