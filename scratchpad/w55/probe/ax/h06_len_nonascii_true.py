# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return len("€")
