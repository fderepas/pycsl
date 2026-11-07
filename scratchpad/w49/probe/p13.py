# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    if "b" < "a":
        return 7
    return 0
