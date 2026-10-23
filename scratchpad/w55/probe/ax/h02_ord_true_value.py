# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 8364
#@ assigns \nothing
def f() -> int:
    return ord("€")
