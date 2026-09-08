# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 0.3
#@ assigns \nothing
def f() -> float:
    return 0.1 + 0.2
