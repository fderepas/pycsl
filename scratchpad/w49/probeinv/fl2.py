# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    if 0.1 + 0.2 > 0.3:
        return 7
    return 0
